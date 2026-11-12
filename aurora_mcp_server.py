"""Aurora MCP Server Lambda - Handles MCP protocol requests for Aurora PostgreSQL."""
import json
import os
import boto3

rds_data = boto3.client("rds-data")


def get_tool_definitions():
    """Load the tool catalog from the bundled tool_definitions.json file.

    The catalog ships as a formatted JSON file alongside this handler so it can be
    edited with normal editor/linting support (instead of a single-line env var).
    """
    definitions_path = os.path.join(os.path.dirname(__file__), "tool_definitions.json")
    with open(definitions_path, "r", encoding="utf-8") as definitions_file:
        return json.load(definitions_file)


def execute_sql(sql):
    """Execute SQL via RDS Data API."""
    cluster_arn = os.environ.get("AURORA_CLUSTER_ARN")
    db_name = os.environ.get("DB_NAME")
    secret_arn = os.environ.get("SECRET_ARN")

    response = rds_data.execute_statement(
        resourceArn=cluster_arn,
        secretArn=secret_arn,
        database=db_name,
        sql=sql,
        includeResultMetadata=True,
    )

    # Convert to simple text output
    columns = [col["name"] for col in response.get("columnMetadata", [])]
    rows = []
    for record in response.get("records", []):
        row = {}
        for i, field in enumerate(record):
            key = columns[i] if i < len(columns) else f"col_{i}"
            for type_key, val in field.items():
                if type_key != "isNull":
                    row[key] = val
                    break
            else:
                row[key] = None
        rows.append(row)

    return rows


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

    try:
        if tool_name == "query":
            # Read parameter name from tool schema definition
            schema_props = tool.get("inputSchema", {}).get("properties", {})
            sql_param_name = list(schema_props.keys())[0] if schema_props else "sql"
            sql = arguments.get(sql_param_name, "")
            if not sql:
                return {"error": f"Missing '{sql_param_name}' parameter"}
            rows = execute_sql(sql)
            return {"content": [{"type": "text", "text": json.dumps(rows, default=str)}]}

        elif tool_name == "describe_table":
            table_name = arguments.get("table_name", "")
            if not table_name:
                return {"error": "Missing 'table_name' parameter"}
            sql = f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table_name}' ORDER BY ordinal_position"
            rows = execute_sql(sql)
            return {"content": [{"type": "text", "text": json.dumps(rows, default=str)}]}

        elif tool_name == "list_tables":
            sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
            rows = execute_sql(sql)
            return {"content": [{"type": "text", "text": json.dumps(rows, default=str)}]}

        elif tool_name == "explain_query":
            schema_props = tool.get("inputSchema", {}).get("properties", {})
            sql_param_name = list(schema_props.keys())[0] if schema_props else "sql"
            sql = arguments.get(sql_param_name, "")
            if not sql:
                return {"error": f"Missing '{sql_param_name}' parameter"}
            explain_sql = f"EXPLAIN {sql}"
            rows = execute_sql(explain_sql)
            return {"content": [{"type": "text", "text": json.dumps(rows, default=str)}]}

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
