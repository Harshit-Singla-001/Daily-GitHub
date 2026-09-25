import json

from google import genai
from google.genai import types

from config import (
    API_KEY,
    MODEL,
    MAX_AGENT_STEPS
)

from tools import execute_tool

client = genai.Client(
    api_key=API_KEY
)

SYSTEM_PROMPT = """
You are a basic AI agent.

Your job is to understand the user's request,
choose the appropriate tool, use the tool,
observe its result, and then answer the user.

Available tools:

1. calculator
Use for mathematical calculations.

2. database_search
Use when the user asks for database records.

Allowed database tables:
- customers
- products
- orders
- order_items

3. database_tables
Use when the user asks which database tables exist.

4. file_search
Use when the user asks for information that may exist
inside local text files.

Rules:

- Choose a tool when the user's request requires it.
- Do not invent database information.
- Do not invent file information.
- Use the calculator for calculations.
- You may use multiple tools when necessary.
- After getting tool results, determine whether another
  tool is needed.
- If no more tools are required, provide the final answer.
"""

tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="calculator",
            description=(
                "Calculate a mathematical expression safely."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "Mathematical expression."
                        )
                    }
                },
                "required": ["expression"]
            }
        ),
        types.FunctionDeclaration(
            name="database_search",
            description=(
                "Search records from a database table."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": (
                            "customers, products, orders, "
                            "or order_items"
                        )
                    },
                    "limit": {
                        "type": "integer",
                        "description": (
                            "Maximum records to return."
                        )
                    }
                },
                "required": ["table"]
            }
        ),
        types.FunctionDeclaration(
            name="database_tables",
            description=(
                "List available database tables."
            ),
            parameters={
                "type": "object",
                "properties": {}
            }
        ),
        types.FunctionDeclaration(
            name="file_search",
            description=(
                "Search information inside local text files."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Text or concept to search."
                        )
                    },
                    "max_results": {
                        "type": "integer",
                        "description": (
                            "Maximum files to return."
                        )
                    }
                },
                "required": ["query"]
            }
        )
    ]
)

CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    tools=[tool]
)

def run_agent(user_input):
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=user_input
                )
            ]
        )
    ]

    steps = []

    for step_number in range(
        1,
        MAX_AGENT_STEPS + 1
    ):
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=CONFIG
        )

        function_calls = (
            response.function_calls
        )

        if not function_calls:
            return {
                "success": True,
                "answer": response.text,
                "steps": steps
            }

        contents.append(
            response.candidates[0].content
        )

        for function_call in function_calls:
            tool_name = function_call.name

            arguments = dict(
                function_call.args or {}
            )

            tool_result = execute_tool(
                tool_name,
                arguments
            )

            steps.append({
                "step": step_number,
                "tool": tool_name,
                "arguments": arguments,
                "result": tool_result
            })

            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_function_response(
                            name=tool_name,
                            response=tool_result
                        )
                    ]
                )
            )

    return {
        "success": False,
        "answer": (
            "The agent reached its maximum "
            "number of steps."
        ),
        "steps": steps
    }