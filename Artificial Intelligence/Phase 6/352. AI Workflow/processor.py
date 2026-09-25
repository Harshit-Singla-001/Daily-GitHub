import ast
import operator
import sqlite3
import os

from config import BASE_DIR

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "database",
    "assistant.db"
)

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos
}

def safe_calculate(expression):
    tree = ast.parse(expression, mode="eval")

    return evaluate_node(tree.body)

def evaluate_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Only numbers are allowed.")

    if isinstance(node, ast.BinOp):
        operation = OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported operator.")

        left = evaluate_node(node.left)
        right = evaluate_node(node.right)

        return operation(left, right)

    if isinstance(node, ast.UnaryOp):
        operation = OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported operator.")

        return operation(
            evaluate_node(node.operand)
        )

    raise ValueError("Invalid mathematical expression.")

def process_calculation(user_input):
    try:
        expression = extract_expression(user_input)

        result = safe_calculate(expression)

        return {
            "success": True,
            "type": "CALCULATION",
            "input": expression,
            "result": result
        }

    except Exception as error:
        return {
            "success": False,
            "type": "CALCULATION",
            "error": str(error)
        }

def extract_expression(user_input):
    expression = user_input.lower()

    prefixes = [
        "calculate",
        "compute",
        "what is",
        "solve"
    ]

    for prefix in prefixes:
        if expression.startswith(prefix):
            expression = expression[len(prefix):].strip()
            break

    return expression

def get_database_data(user_input):
    try:
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        table = detect_table(user_input)

        if not table:
            connection.close()

            return {
                "success": False,
                "type": "DATABASE",
                "error": "Could not identify a database table."
            }

        cursor.execute(
            f"SELECT * FROM {table} LIMIT 20"
        )

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]

        connection.close()

        return {
            "success": True,
            "type": "DATABASE",
            "table": table,
            "columns": columns,
            "rows": [dict(row) for row in rows]
        }

    except Exception as error:
        return {
            "success": False,
            "type": "DATABASE",
            "error": str(error)
        }

def detect_table(user_input):
    text = user_input.lower()

    table_mapping = {
        "customers": ["customer", "customers"],
        "products": ["product", "products"],
        "orders": ["order", "orders"],
        "order_items": [
            "order item",
            "order items",
            "order_item",
            "order_items"
        ]
    }

    for table, keywords in table_mapping.items():
        for keyword in keywords:
            if keyword in text:
                return table

    return None

from google import genai
from config import API_KEY, MODEL

client = genai.Client(api_key=API_KEY)

def process_question(user_input):
    response = client.models.generate_content(
        model=MODEL,
        contents=f"""
Explain the following question clearly and accurately.

Question:
{user_input}
"""
    )

    return {
        "success": True,
        "type": "QUESTION",
        "result": response.text
    }

def process_general(user_input):
    response = client.models.generate_content(
        model=MODEL,
        contents=user_input
    )

    return {
        "success": True,
        "type": "GENERAL",
        "result": response.text
    }