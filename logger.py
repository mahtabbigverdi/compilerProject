from anytree import RenderTree


class Logger:
    __instance = None

    def __init__(self):
        if Logger.__instance:
            raise Exception('This class is a singleton!')
        self.tokens = {}
        self.lexical_errors = {}
        self.syntax_errors = {}
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
        if line in self.lexical_errors:
            self.lexical_errors[line].append((token, err))
        else:
            self.lexical_errors[line] = [(token, err)]

    def log_syntax_error(self, line, err):
        if line in self.syntax_errors:
            self.syntax_errors[line].append(err)
        else:
            self.syntax_errors[line] = [err]

    def save_lexical_errors(self):
        log = ''
        if self.lexical_errors:
            for line, error_list in self.lexical_errors.items():
                log += f'{line}.\t'
                for token, error in error_list:
                    log += f'({token}, {error}) '
                log = log[:-1]
                log += '\n'
            log = log[:-1]
        else:
            log = 'There is no lexical error.'
        with open('output/lexical_errors.txt', 'w') as file:
            file.write(log)

    def save_syntax_errors(self):
        log = ''
        if self.syntax_errors:
            for line, error_list in self.syntax_errors.items():
                for err in error_list:
                    log += f'#{line} : syntax error, {err}\n'
            log = log[:-1]
        else:
            log = 'There is no syntax error.'
        with open('output/syntax_errors.txt', 'w') as file:
            file.write(log)

    def save_symbol_table(self, symbol_table):
        log = ''
        for i, lexeme in enumerate(symbol_table):
            log += f'{i + 1}.\t{lexeme}\n'
        log = log[:-1]
        with open('output/symbol_table.txt', 'w') as file:
            file.write(log)

    def save_tokens(self):
        log = ''
        for line, token_list in self.tokens.items():
            log += f'{line}.\t'
            for token_type, lexeme in token_list:
                log += f'({token_type}, {lexeme}) '
            log = log[:-1]
            log += '\n'
        if log:
            log = log[:-1]
        with open('output/tokens.txt', 'w') as file:
            file.write(log)

    def save_parse_tree(self, root):
        log = ''
        for pre, fill, node in RenderTree(root):
            # print(root)
            log += '%s%s\n' % (pre, node.name)
        with open('output/parse_tree.txt', 'w') as file:
            file.write(log)

    def save_program_block(self, PB):
        log = ''
        for i, program in enumerate(PB):
            log += f'{i + 1}\t{program}\n'
        log = log[:-1]
        with open('output/output.txt', 'w') as file:
            file.write(log)
