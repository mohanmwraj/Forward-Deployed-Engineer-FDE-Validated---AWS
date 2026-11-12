"""LangGraph Agent Lambda - Agentic AI with DynamoDB checkpointing.

Uses LangGraph StateGraph with tool nodes for:
- query_customers: SQL queries against Aurora PostgreSQL
- search_documents: RAG retrieval via Bedrock Knowledge Base

State is persisted via DynamoDBSaver so the agent remembers
prior conversations across invocations.
"""
import json
import os
import time
import boto3
from typing import Annotated, TypedDict, Literal

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph_checkpoint_aws import DynamoDBSaver

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_aws import ChatBedrockConverse


# ============================================================================
# CONFIGURATION
# ============================================================================
MODEL_ID = os.environ.get("MODEL_ID", "us.amazon.nova-pro-v1:0")
CHECKPOINT_TABLE = os.environ.get("CHECKPOINT_TABLE_NAME", "agent-checkpoints")
REGION = os.environ.get("AWS_REGION_OVERRIDE", "us-east-1")
AURORA_TOOL_FUNCTION = os.environ.get("AURORA_TOOL_FUNCTION", "")
KB_RETRIEVE_FUNCTION = os.environ.get("KB_RETRIEVE_FUNCTION", "")

lambda_client = boto3.client("lambda", region_name=REGION)


# ============================================================================
# STATE DEFINITION
# ============================================================================
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# ============================================================================
# TOOL DEFINITIONS (for Bedrock Converse API)
# ============================================================================
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_customers",
            "description": "Execute a SQL query against the Aurora PostgreSQL database to get customer data, order information, or aggregated summaries. Use this for questions about customers, regions, revenue, or orders.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to execute. Available tables and columns: customers (id, name, email, region, tier, total_orders, order_count, last_purchase); orders (id, customer_id, amount, status, product_category, order_date, shipped_date); customer_summary (region, customer_count, total_orders, avg_orders, most_recent_purchase). The orders table has NO region column — to filter or group orders by region or tier, JOIN orders to customers ON orders.customer_id = customers.id. For region-level spend summaries, prefer the customer_summary view."
                    }
                },
                "required": ["sql"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search company documents (policies, product catalogs) using semantic search. Use this for questions about return policies, shipping, privacy, products, pricing, features, or integrations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query to find relevant documents."
                    }
                },
                "required": ["query"]
            }
        }
    }
]


# ============================================================================
# TOOL EXECUTION
# ============================================================================
def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool by invoking the corresponding Lambda function."""
    try:
        if tool_name == "query_customers":
            response = lambda_client.invoke(
                FunctionName=AURORA_TOOL_FUNCTION,
                Payload=json.dumps({
                    "action": "query",
                    "sql": tool_input.get("sql", "")
                }),
            )
            result = json.loads(response["Payload"].read())
            if result.get("statusCode") == 200:
                return json.dumps(result.get("rows", []), default=str)
            else:
                return f"Error: {result.get('error', 'Unknown error')}"

        elif tool_name == "search_documents":
            # Invoke KB Retrieve Tool Lambda
            response = lambda_client.invoke(
                FunctionName=KB_RETRIEVE_FUNCTION,
                Payload=json.dumps({
                    "query": tool_input.get("query", ""),
                    "max_results": 3,
                }),
            )
            result = json.loads(response["Payload"].read())
            if result.get("statusCode") == 200:
                chunks = [r.get("content", "") for r in result.get("results", [])]
                return "\n\n---\n\n".join(chunks) if chunks else "No relevant documents found."
            else:
                return f"Error: {result.get('error', 'Unknown error')}"

        else:
            return f"Unknown tool: {tool_name}"

    except Exception as e:
        return f"Tool execution error: {str(e)}"


# ============================================================================
# GRAPH NODES
# ============================================================================
def call_model(state: AgentState) -> AgentState:
    """Call the LLM with current messages and tool definitions."""
    model = ChatBedrockConverse(
        model=MODEL_ID,
        region_name=REGION,
        max_tokens=1024,
    )
    model_with_tools = model.bind_tools(TOOLS)

    # Filter out messages with empty content before sending to Converse API
    # (can happen when loading checkpoints with reasoning-only responses)
    filtered_messages = []
    for msg in state["messages"]:
        if hasattr(msg, "content"):
            # If content is a list, check if it has any text blocks
            if isinstance(msg.content, list):
                text_blocks = [b for b in msg.content if isinstance(b, dict) and b.get("type") == "text" and b.get("text")]
                if not text_blocks and not getattr(msg, "tool_calls", None):
                    # Reasoning-only response — add a placeholder text
                    msg.content = "I'm thinking about this..."
            elif isinstance(msg.content, str) and not msg.content.strip() and not getattr(msg, "tool_calls", None):
                msg.content = "I'm thinking about this..."
        filtered_messages.append(msg)

    response = model_with_tools.invoke(filtered_messages)

    # Ensure the response has non-empty content for checkpoint serialization
    if isinstance(response.content, list):
        text_blocks = [b for b in response.content if isinstance(b, dict) and b.get("type") == "text" and b.get("text")]
        if not text_blocks and not response.tool_calls:
            # Extract reasoning text if available, use as content
            reasoning_blocks = [b for b in response.content if isinstance(b, dict) and b.get("type") == "reasoning_content"]
            if reasoning_blocks:
                reasoning_text = reasoning_blocks[0].get("reasoning_content", {}).get("text", "")
                response.content = reasoning_text or "I understand."
            else:
                response.content = "I understand."
    elif isinstance(response.content, str) and not response.content.strip() and not response.tool_calls:
        response.content = "I understand."

    return {"messages": [response]}


def call_tools(state: AgentState) -> AgentState:
    """Execute tool calls from the model's response."""
    last_message = state["messages"][-1]
    tool_messages = []

    for tool_call in last_message.tool_calls:
        result = execute_tool(tool_call["name"], tool_call["args"])
        tool_messages.append(
            ToolMessage(content=result, tool_call_id=tool_call["id"])
        )

    return {"messages": tool_messages}


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """Decide whether to call tools or end."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"


# ============================================================================
# BUILD GRAPH
# ============================================================================
def build_graph():
    """Construct the LangGraph StateGraph."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("agent", call_model)
    graph.add_node("tools", call_tools)

    # Add edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {
        "tools": "tools",
        "end": END,
    })
    graph.add_edge("tools", "agent")

    return graph


# ============================================================================
# LAMBDA HANDLER
# ============================================================================
def handler(event, context):
    """LangGraph agent handler with DynamoDB checkpointing."""
    # Handle API Gateway proxy integration (body is a JSON string)
    if "body" in event and isinstance(event.get("body"), str):
        try:
            body = json.loads(event["body"])
        except (json.JSONDecodeError, TypeError):
            body = {}
    else:
        body = event

    thread_id = body.get("thread_id") or f"thread_{int(time.time())}"
    message = body.get("message", "")

    if not message:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Missing 'message' parameter"}),
        }

    try:
        # Build the graph and persist state with the DynamoDB checkpointer.
        # State is saved by langgraph-checkpoint-aws DynamoDBSaver. The backing table's
        # key schema, TTL attribute, and billing mode are defined by that library — see the
        # documentation for the required table structure:
        # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ddb-langgraph-checkpoint.html
        graph = build_graph()
        checkpointer = DynamoDBSaver(
            table_name=CHECKPOINT_TABLE,
            region_name=REGION,
        )
        app = graph.compile(checkpointer=checkpointer)

        # Invoke with thread config for state persistence
        config = {"configurable": {"thread_id": thread_id}}
        input_state = {"messages": [HumanMessage(content=message)]}

        # Run the agent
        result = app.invoke(input_state, config=config)

        # Extract the final response as clean text.
        # Nova Pro may return content as a list of blocks (e.g., a reasoning_content
        # block plus a text block). Surface only the text to the user — never the
        # chain-of-thought or the raw block structure.
        final_message = result["messages"][-1]
        raw_content = getattr(final_message, "content", final_message)

        if isinstance(raw_content, list):
            text_parts = []
            for block in raw_content:
                if isinstance(block, dict):
                    # keep only text blocks; skip reasoning_content and other block types
                    if block.get("type") == "text" and block.get("text"):
                        text_parts.append(block["text"])
                elif isinstance(block, str):
                    text_parts.append(block)
            response_text = "".join(text_parts).strip()
            if not response_text:
                # Fallback: no text block present (reasoning-only) — return a generic message
                response_text = "I don't have a response for that."
        elif isinstance(raw_content, str):
            response_text = raw_content.strip()
        else:
            response_text = str(raw_content)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "thread_id": thread_id,
                "response": response_text,
            }),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "error": f"Agent error: {str(e)}",
                "thread_id": thread_id,
            }),
        }
