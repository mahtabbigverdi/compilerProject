keywords = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return', 'for']


class Scanner:
    def __init__(self, symbol_table):
        self.prog = ''
        self.symbol_table = symbol_table
        self.ptr = 0
        self.line_no = 1
        self.tokens = {}

    def set_prog(self, prog):
        self.prog = prog

    def get_next_token(self):
        pass

    def add_token(self, token_type, lexeme):
        if self.line_no in self.tokens:
            self.tokens[self.line_no].append((token_type, lexeme))
        else:
            self.tokens[self.line_no] = [(token_type, lexeme)]
