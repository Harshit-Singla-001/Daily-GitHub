import ast
import operator


OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos
}


def safe_calculate(expression):
    if not isinstance(
        expression,
        str
    ):
        raise ValueError(
            "Expression must be text."
        )

    expression = expression.strip()

    if not expression:
        raise ValueError(
            "Expression cannot be empty."
        )

    if len(expression) > 200:
        raise ValueError(
            "Expression is too long."
        )

    tree = ast.parse(
        expression,
        mode="eval"
    )

    result = evaluate_node(
        tree.body
    )

    if isinstance(
        result,
        complex
    ):
        raise ValueError(
            "Complex results are not supported."
        )

    return result


def evaluate_node(node):
    if isinstance(
        node,
        ast.Constant
    ):
        if isinstance(
            node.value,
            (int, float)
        ):
            return node.value

        raise ValueError(
            "Only numbers are allowed."
        )

    if isinstance(
        node,
        ast.BinOp
    ):
        left = evaluate_node(
            node.left
        )

        right = evaluate_node(
            node.right
        )

        operation = OPERATORS.get(
            type(node.op)
        )

        if operation is None:
            raise ValueError(
                "Unsupported mathematical operation."
            )

        if (
            isinstance(
                node.op,
                ast.Pow
            )
            and abs(right) > 10
        ):
            raise ValueError(
                "Exponent is too large."
            )

        return operation(
            left,
            right
        )

    if isinstance(
        node,
        ast.UnaryOp
    ):
        value = evaluate_node(
            node.operand
        )

        operation = OPERATORS.get(
            type(node.op)
        )

        if operation is None:
            raise ValueError(
                "Unsupported unary operation."
            )

        return operation(
            value
        )

    raise ValueError(
        "Invalid mathematical expression."
    )