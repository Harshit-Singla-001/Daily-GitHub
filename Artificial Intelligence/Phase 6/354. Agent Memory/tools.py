from calculator_tool import calculate
from database_tool import search_database, list_tables
from file_tool import search_files


TOOLS = {
    "calculator": calculate,
    "database_search": search_database,
    "database_tables": list_tables,
    "file_search": search_files
}


def execute_tool(tool_name, arguments):
    if tool_name not in TOOLS:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }

    try:
        return TOOLS[tool_name](**arguments)

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }