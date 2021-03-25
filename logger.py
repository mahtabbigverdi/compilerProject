class Logger:

    __instance = None

    def __init__(self):
        if Logger.__instance:
            raise Exception('This class is a singleton!')
        self.tokens = {}
        self.lexical_errors = []
        Logger.__instance = self

    @staticmethod
    def get_instance():
        if Logger.__instance:
            return Logger.__instance
        return Logger()

    def add_token(self, line_no, token_type, lexeme):
        if line_no in self.tokens:
            self.tokens[line_no].append((token_type, lexeme))
        else:
            self.tokens[line_no] = [(token_type, lexeme)]

    def log_lexical_error(self, line, token, err):
        self.lexical_errors.append((line, token, err))

    def save_lexical_errors(self):
        log = ''
        if not self.lexical_errors:
            log = 'There is no lexical error.'
        else:
            for line, token, err in self.lexical_errors:
                log += f'{line}.\t({token}, {err})\n'
        with open('output/lexical_errors.txt', 'w') as file:
            file.write(log)

    def save_symbol_table(self, symbol_table):
        log = ''
        for i, lexeme in enumerate(symbol_table):
            log += f'{i + 1}.\t{lexeme}\n'

    def save_tokens(self):
        log = ''
        for line, token_list in self.tokens.items():
            log += f'{line}.\t'
            for token_type, lexeme in token_list:
                log += f'({token_type}, {lexeme}) '
            log += '\n'