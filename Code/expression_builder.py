"""
expression_builder.py
builds the math expression step by step when player taps buttons
"""


class ExpressionBuilder:

    def __init__(self):
        self._tokens = []  # list of numbers and operators the player has entered

    def add_token(self, token: str):
        # add one number or operator to the expression
        self._tokens.append(token)

    def undo(self):
        # remove last token (like backspace)
        if self._tokens:
            self._tokens.pop()

    def clear(self):
        # clear everything and start over
        self._tokens.clear()

    def get_expression(self) -> str:
        # return expression without spaces (used for calculation)
        return "".join(self._tokens)

    def get_display(self) -> str:
        # return expression with spaces (shown on screen)
        return " ".join(self._tokens)

    def is_empty(self) -> bool:
        # check if player hasn't entered anything yet
        return len(self._tokens) == 0

    def token_count(self) -> int:
        # how many tokens are in the expression right now
        return len(self._tokens)
