from google import genai
from google.genai import types

from config import API_KEY, MODEL
from tools import calculator, database_search, file_search, database_tables

client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = """
You are an AI assistant with access to Python tools.

Available tools:

1. calculator
Use this for mathematical calculations.

2. database_search
Use this when the user asks about customers, products, orders,
or order items stored in the SQLite database.

3. file_search
Use this when the user asks about information stored in local files.

4. database_tables
Use this when the user asks which tables exist in the database.

Rules:
- Use a tool whenever the user's request requires external information.
- Do not invent database records.
- Do not invent information from files.
- After receiving a tool result, explain the result clearly.
"""

calculator_declaration = types.FunctionDeclaration(
    name="calculator",
    description="Calculate mathematical expressions safely.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression such as 25 * 4 + 10"
            }
        },
        "required": ["expression"]
    }
)

database_search_declaration = types.FunctionDeclaration(
    name="database_search",
    description=(
        "Search records from the SQLite database. "
        "Use for customers, products, orders and order_items."
    ),
    parameters={
        "type": "object",
        "properties": {
            "table": {
                "type": "string",
                "description": (
                    "Database table name. "
                    "Allowed tables: customers, products, orders, order_items."
                )
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of records to return."
            }
        },
        "required": ["table"]
    }
)

file_search_declaration = types.FunctionDeclaration(
    name="file_search",
    description="Search information inside local text files.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Text or concept to search for."
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of files to return."
            }
        },
        "required": ["query"]
    }
)

database_tables_declaration = types.FunctionDeclaration(
    name="database_tables",
    description="List all available tables in the SQLite database.",
    parameters={
        "type": "object",
        "properties": {}
    }
)

tool = types.Tool(
    function_declarations=[
        calculator_declaration,
        database_search_declaration,
        file_search_declaration,
        database_tables_declaration
    ]
)

config = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    tools=[tool]
)

def execute_tool(function_name, arguments):
    if function_name == "calculator":
        return calculator(
            arguments.get("expression", "")
        )

    if function_name == "database_search":
        return database_search(
            arguments.get("table", ""),
            arguments.get("limit", 20)
        )

    if function_name == "file_search":
        return file_search(
            arguments.get("query", ""),
            arguments.get("max_results", 5)
        )

    if function_name == "database_tables":
        return database_tables()

    return {
        "success": False,
        "error": f"Unknown tool: {function_name}"
    }

def ask_assistant(question):
    response = client.models.generate_content(
        model=MODEL,
        contents=question,
        config=config
    )

    if not response.function_calls:
        return {
            "answer": response.text,
            "tool_used": None,
            "tool_result": None
        }

    function_call = response.function_calls[0]

    tool_name = function_call.name
    tool_arguments = dict(function_call.args)

    tool_result = execute_tool(
        tool_name,
        tool_arguments
    )

    function_response_part = types.Part.from_function_response(
        name=tool_name,
        response=tool_result
    )

    final_response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=question
                    )
                ]
            ),
            response.candidates[0].content,
            types.Content(
                role="user",
                parts=[
                    function_response_part
                ]
            )
        ],
        config=config
    )

    return {
        "answer": final_response.text,
        "tool_used": tool_name,
        "tool_result": tool_result
    }