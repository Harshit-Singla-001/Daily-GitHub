import ast
import operator

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

def calculate(expression):
    try:
        expression = expression.strip()

        if not expression:
            return {
                "success": False,
                "error": "Expression is empty."
            }

        tree = ast.parse(
            expression,
            mode="eval"
        )

        result = evaluate_node(tree.body)

        return {
            "success": True,
            "expression": expression,
            "result": result
        }

    except ZeroDivisionError:
        return {
            "success": False,
            "error": "Division by zero is not allowed."
        }

    except Exception as error:
        return {
            "success": False,
            "error": f"Invalid expression: {error}"
        }

def evaluate_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Only numbers are allowed.")

    if isinstance(node, ast.BinOp):
        operation = OPERATORS.get(
            type(node.op)
        )

        if operation is None:
            raise ValueError(
                "Unsupported mathematical operator."
            )

        left = evaluate_node(node.left)
        right = evaluate_node(node.right)

        return operation(left, right)

    if isinstance(node, ast.UnaryOp):
        operation = OPERATORS.get(
            type(node.op)
        )

        if operation is None:
            raise ValueError(
                "Unsupported unary operator."
            )

        return operation(
            evaluate_node(node.operand)
        )

    raise ValueError(
        "Unsupported mathematical expression."
    )