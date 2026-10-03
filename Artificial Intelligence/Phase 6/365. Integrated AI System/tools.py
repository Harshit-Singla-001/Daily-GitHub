from calculator_tool import safe_calculate
from database_tool import (
    list_tables,
    search_database
)
from file_tool import search_files


def execute_tool(
    tool_name,
    arguments
):
    arguments = arguments or {}

    if tool_name == "calculator":
        expression = arguments.get(
            "expression"
        )

        return {
            "tool": "calculator",
            "result": safe_calculate(
                expression
            )
        }

    if tool_name == "database_tables":
        return {
            "tool": "database_tables",
            "result": list_tables()
        }

    if tool_name == "database_search":
        table_name = arguments.get(
            "table_name"
        )

        limit = arguments.get(
            "limit",
            20
        )

        return {
            "tool": "database_search",
            "result": search_database(
                table_name,
                limit
            )
        }

    if tool_name == "file_search":
        query = arguments.get(
            "query"
        )

        return {
            "tool": "file_search",
            "result": search_files(
                query
            )
        }

    raise ValueError(
        f"Unknown tool: {tool_name}"
    )