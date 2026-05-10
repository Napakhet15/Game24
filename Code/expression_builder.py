class ExpressionBuilder:

    def __init__(self):
        self._tokens = []  # list numbers operators

    def add_token(self, token: str):
        # add one to the expression
        self._tokens.append(token)

    def undo(self):
        # remove last 
        if self._tokens:
            self._tokens.pop()

    def clear(self):
        # clear 
        self._tokens.clear()

    def get_expression(self) -> str:
        # return 
        return "".join(self._tokens)

    def get_display(self) -> str:
        # return
        return " ".join(self._tokens)

    def is_empty(self) -> bool:
        return len(self._tokens) == 0

    def token_count(self) -> int:
        return len(self._tokens)
