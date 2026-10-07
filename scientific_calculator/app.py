from flask import Flask, render_template, request
import ast
import math
import operator

app = Flask(__name__)

FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log10,
    "sqrt": math.sqrt,
}

BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}

UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def calculate_expression(expression):
    expression = expression.replace("×", "*").replace("÷", "/").replace("−", "-")
    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
            left = evaluate(node.left)
            right = evaluate(node.right)
            return BIN_OPS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
            return UNARY_OPS[type(node.op)](evaluate(node.operand))

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id not in FUNCTIONS or len(node.args) != 1:
                raise ValueError
            return FUNCTIONS[node.func.id](evaluate(node.args[0]))

        raise ValueError

    result = evaluate(tree)

    if not math.isfinite(result):
        raise ValueError

    return result


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    error = None
    expression = ""

    if request.method == "POST":
        expression = request.form.get("expression", "").strip()

        if not expression:
            error = "Enter an expression."
        else:
            try:
                result = calculate_expression(expression)
            except (ValueError, TypeError, SyntaxError, ZeroDivisionError, OverflowError):
                error = "Invalid expression."

    return render_template(
        "index.html",
        result=result,
        error=error,
        expression=expression,
    )


if __name__ == "__main__":
    app.run(debug=True)
