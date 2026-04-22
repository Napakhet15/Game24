"""
math_engine.py
evaluates the player's math expression safely using AST
we use AST instead of eval() because eval() is dangerous
"""

import ast
import math
import operator


class MathEngine:

    # allowed binary operators
    BINARY_OPS = {
        ast.Add:  operator.add,
        ast.Sub:  operator.sub,
        ast.Mult: operator.mul,
        ast.Div:  operator.truediv,
        ast.Pow:  operator.pow,
    }

    # allowed unary operators
    UNARY_OPS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def __init__(self, advanced_mode=False):
        # advanced_mode enables ^ and sqrt
        self.advanced_mode = advanced_mode

    def evaluate(self, expression: str):
        # evaluate expression string and return float result
        # raises ValueError if expression is invalid

        # reject very long expressions just in case
        if len(expression) > 100:
            raise ValueError("Expression is too long (max 100 characters)")

        # replace ^ with ** so python can parse it
        expression = expression.replace("^", "**")

        # parse into AST tree
        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError:
            raise ValueError(f"Invalid expression syntax: {expression}")

        # walk the tree and calculate
        result = self._eval_node(tree.body)
        return result

    def _eval_node(self, node):
        # handle each type of node in the AST tree

        # plain number like 3 or 5.0
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError(f"Unsupported constant: {node.value}")

        # for older python versions
        elif isinstance(node, ast.Num):
            return float(node.n)

        # binary operation like 3 + 5
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)

            # check operator is allowed
            if op_type not in self.BINARY_OPS:
                raise ValueError(f"Unsupported operator: {op_type}")

            # power only allowed in advanced mode
            if op_type == ast.Pow and not self.advanced_mode:
                raise ValueError("Power operator not allowed in this mode")

            # evaluate both sides first
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)

            # check for division by zero
            if op_type == ast.Div:
                if abs(right) < 1e-9:
                    raise ValueError("Division by zero")

            # prevent very large power results
            if op_type == ast.Pow:
                if abs(left) > 1e6 or abs(right) > 10:
                    raise ValueError("Power operands too large")

            return self.BINARY_OPS[op_type](left, right)

        # unary like -3 or +3
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self.UNARY_OPS:
                raise ValueError(f"Unsupported unary operator: {op_type}")
            operand = self._eval_node(node.operand)
            return self.UNARY_OPS[op_type](operand)

        # function call - only sqrt allowed in advanced mode
        elif isinstance(node, ast.Call):
            if not self.advanced_mode:
                raise ValueError("Function calls not allowed in this mode")

            if not isinstance(node.func, ast.Name):
                raise ValueError("Only named functions allowed")

            func_name = node.func.id

            if func_name != "sqrt":
                raise ValueError(f"Unsupported function: {func_name}")

            if len(node.args) != 1:
                raise ValueError("sqrt() requires exactly one argument")

            arg = self._eval_node(node.args[0])

            # sqrt of negative number is not real
            if arg < 0:
                raise ValueError("sqrt of negative number is not allowed")

            return math.sqrt(arg)

        else:
            raise ValueError(f"Unsupported expression node: {type(node)}")

    def equals_target(self, expression: str, target: float) -> bool:
        # check if expression equals target, return False if any error
        try:
            result = self.evaluate(expression)
            return abs(result - target) < 1e-6
        except (ValueError, ZeroDivisionError, OverflowError):
            return False
