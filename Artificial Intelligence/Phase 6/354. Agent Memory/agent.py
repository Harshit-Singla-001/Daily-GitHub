from google import genai
from google.genai import types

from config import API_KEY, MODEL, MAX_AGENT_STEPS
from tools import execute_tool
from memory import (
    add_short_term_message,
    save_conversation,
    build_memory_context
)

client = genai.Client(api_key=API_KEY)


SYSTEM_PROMPT = """
You are an AI agent with conversation memory and access to tools.

Available tools:
1. calculator
2. database_search
3. database_tables
4. file_search

You should:
- Understand the user's request.
- Use tools when necessary.
- Use recent conversation context when answering follow-up questions.
- Use persistent user memory when it is relevant.
- Do not invent database or file information.
- Clearly explain the result of tool calls.
- If a tool is unnecessary, answer directly.
- Keep responses concise but useful.
"""


calculator_declaration = types.FunctionDeclaration(
    name="calculator",
    description="Calculate a mathematical expression safely.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression such as 25 * 4"
            }
        },
        "required": ["expression"]
    }
)


database_search_declaration = types.FunctionDeclaration(
    name="database_search",
    description="Search rows from an allowed database table.",
    parameters={
        "type": "object",
        "properties": {
            "table": {
                "type": "string",
                "description": "Database table name"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of rows"
            }
        },
        "required": ["table"]
    }
)


database_tables_declaration = types.FunctionDeclaration(
    name="database_tables",
    description="List available database tables.",
    parameters={
        "type": "object",
        "properties": {}
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
                "description": "Text to search for"
            }
        },
        "required": ["query"]
    }
)


tool = types.Tool(
    function_declarations=[
        calculator_declaration,
        database_search_declaration,
        database_tables_declaration,
        file_search_declaration
    ]
)


CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    tools=[tool]
)


def run_agent(user_id, user_input):
    memory_context = build_memory_context(user_id)

    if memory_context:
        prompt = f"""
Here is the memory available for this user:

{memory_context}

CURRENT USER REQUEST:
{user_input}
"""
    else:
        prompt = user_input

    add_short_term_message(
        user_id,
        "user",
        user_input
    )

    save_conversation(
        user_id,
        "user",
        user_input
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt)
            ]
        )
    ]

    steps = []

    for step_number in range(1, MAX_AGENT_STEPS + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=CONFIG
            )

            function_calls = response.function_calls

            if not function_calls:
                answer = response.text or "I could not generate a response."

                add_short_term_message(
                    user_id,
                    "assistant",
                    answer
                )

                save_conversation(
                    user_id,
                    "assistant",
                    answer
                )

                return {
                    "success": True,
                    "answer": answer,
                    "steps": steps
                }

            contents.append(response.candidates[0].content)

            for function_call in function_calls:
                tool_name = function_call.name
                arguments = dict(function_call.args or {})

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

        except Exception as error:
            return {
                "success": False,
                "answer": f"Agent error: {error}",
                "steps": steps
            }

    return {
        "success": False,
        "answer": "The agent reached its maximum number of steps.",
        "steps": steps
    }