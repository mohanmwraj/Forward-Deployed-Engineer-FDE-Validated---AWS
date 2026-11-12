"""DynamoDB MCP Server Lambda - Handles MCP protocol requests for DynamoDB."""
import json
import os
import boto3

region = os.environ.get("AWS_REGION_OVERRIDE", "us-east-1")
dynamodb = boto3.client("dynamodb", region_name=region)


def get_tool_definitions():
    """Load the tool catalog from the bundled tool_definitions.json file.

    The catalog ships as a formatted JSON file alongside this handler so it can be
    edited with normal editor/linting support (instead of a single-line env var).
    """
    definitions_path = os.path.join(os.path.dirname(__file__), "tool_definitions.json")
    with open(definitions_path, "r", encoding="utf-8") as definitions_file:
        return json.load(definitions_file)


def handle_tools_list():
    """Return the tool catalog."""
    tools = get_tool_definitions()
    return {"tools": tools}


def handle_tools_call(params):
    """Execute a tool call."""
    tool_name = params.get("name", "")
    arguments = params.get("arguments", {})
    tools = get_tool_definitions()

    # Find the tool
    tool = next((t for t in tools if t["name"] == tool_name), None)
    if not tool:
        return {"error": f"Tool not found: {tool_name}"}

    table_names = os.environ.get("TABLE_NAMES", "").split(",")

    try:
        if tool_name == "describe_table":
            table_name = arguments.get("table_name", "")
            if not table_name:
                return {"error": "Missing 'table_name' parameter"}
            response = dynamodb.describe_table(TableName=table_name)
            table = response["Table"]
            result = {
                "table_name": table["TableName"],
                "key_schema": [{"name": k["AttributeName"], "type": k["KeyType"]} for k in table["KeySchema"]],
                "attribute_definitions": [{"name": a["AttributeName"], "type": a["AttributeType"]} for a in table["AttributeDefinitions"]],
                "item_count": table.get("ItemCount", 0),
                "status": table["TableStatus"],
                "billing_mode": table.get("BillingModeSummary", {}).get("BillingMode", "PROVISIONED"),
            }
            if "GlobalSecondaryIndexes" in table:
                result["gsi"] = [{"name": g["IndexName"], "key_schema": g["KeySchema"]} for g in table["GlobalSecondaryIndexes"]]
            return {"content": [{"type": "text", "text": json.dumps(result, default=str)}]}

        elif tool_name == "sample_items":
            table_name = arguments.get("table_name", "")
            max_results = arguments.get("max_results", 5)
            if not table_name:
                return {"error": "Missing 'table_name' parameter"}
            if not isinstance(max_results, int):
                return {"error": f"'max_results' must be integer, got {type(max_results).__name__}"}
            response = dynamodb.scan(TableName=table_name, Limit=max_results)
            items = response.get("Items", [])
            return {"content": [{"type": "text", "text": json.dumps(items, default=str)}]}

        elif tool_name == "list_tables":
            response = dynamodb.list_tables()
            tables = response.get("TableNames", [])
            # Filter to configured tables
            configured = [t for t in tables if t in table_names]
            return {"content": [{"type": "text", "text": json.dumps({"tables": configured})}]}

        elif tool_name == "analyze_access_patterns":
            table_name = arguments.get("table_name", "")
            if not table_name:
                return {"error": "Missing 'table_name' parameter"}

            # Describe table
            response = dynamodb.describe_table(TableName=table_name)
            table = response["Table"]

            # Describe TTL
            ttl_response = dynamodb.describe_time_to_live(TableName=table_name)
            ttl_spec = ttl_response.get("TimeToLiveDescription", {})

            # Build analysis
            analysis = {
                "table_name": table["TableName"],
                "partition_key": next((k["AttributeName"] for k in table["KeySchema"] if k["KeyType"] == "HASH"), None),
                "sort_key": next((k["AttributeName"] for k in table["KeySchema"] if k["KeyType"] == "RANGE"), None),
                "billing_mode": table.get("BillingModeSummary", {}).get("BillingMode", "PROVISIONED"),
                "ttl_attribute": ttl_spec.get("AttributeName") if ttl_spec.get("TimeToLiveStatus") == "ENABLED" else None,
                "ttl_status": ttl_spec.get("TimeToLiveStatus", "DISABLED"),
            }

            # GSIs
            if "GlobalSecondaryIndexes" in table:
                analysis["global_secondary_indexes"] = []
                for gsi in table["GlobalSecondaryIndexes"]:
                    gsi_info = {
                        "name": gsi["IndexName"],
                        "partition_key": next((k["AttributeName"] for k in gsi["KeySchema"] if k["KeyType"] == "HASH"), None),
                        "sort_key": next((k["AttributeName"] for k in gsi["KeySchema"] if k["KeyType"] == "RANGE"), None),
                    }
                    analysis["global_secondary_indexes"].append(gsi_info)

            return {"content": [{"type": "text", "text": json.dumps(analysis, default=str)}]}

        else:
            return {"error": f"Tool '{tool_name}' not implemented"}

    except Exception as e:
        return {"error": str(e)}


def handler(event, context):
    """MCP protocol handler."""
    method = event.get("method", "")

    if method == "tools/list":
        return handle_tools_list()
    elif method == "tools/call":
        params = event.get("params", {})
        return handle_tools_call(params)
    else:
        return {"error": f"Unknown method: {method}"}
