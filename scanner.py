from logger import Logger

keywords = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return', 'for']


class Scanner:
    def __init__(self, symbol_table):
        self.prog = ''
        self.symbol_table = symbol_table
        self.ptr = 0
        self.line_no = 1
        self.logger = Logger.get_instance()

    def is_keyword(self, lexeme):
        return lexeme in keywords

    def is_finished(self, pointer):
        return pointer >= len(self.prog)

    def set_prog(self, prog):
        self.prog = prog

    def is_valid(self, character):
        return character.isalpha() or character.isdigit() \
               or character in \
               [',', ';', ':', '[', ']', '(', ')', '{', '}', '+', '-', '<', ' ', '\n', '\t', '\r', '\f', '\v', '=', '*', '/']

    def get_next_token(self):
        end = self.ptr
        token_type = ''
        lexeme = None
        ## ID/Keyword DFA
        if self.prog[self.ptr].isalpha():
            while self.prog[end].isalpha() or self.prog[end].isdigit():
                end += 1
                if self.is_finished(end):
                    lexeme = self.prog[self.ptr:end]
                    token_type = 'KEYWORD' if self.is_keyword(lexeme) else 'ID'
                    if lexeme not in self.symbol_table:
                        self.symbol_table.append(lexeme)
                    self.ptr = end
                    return token_type, lexeme

            if self.is_valid(self.prog[end]):
                lexeme = self.prog[self.ptr:end]
                token_type = 'KEYWORD' if self.is_keyword(lexeme) else 'ID'
                if lexeme not in self.symbol_table:
                    self.symbol_table.append(lexeme)
                self.ptr = end
                return token_type, lexeme
            else:
                self.logger.log_lexical_error(self.line_no, self.prog[self.ptr:end + 1], 'Invalid input')
                self.ptr = end + 1
                return None

        # digit DFA
        elif self.prog[self.ptr].isdigit():
            while self.prog[end].isdigit():
                end += 1
                if self.is_finished(end):
                    lexeme = self.prog[self.ptr:end]
                    token_type = 'NUM'
                    self.ptr = end
                    return token_type, lexeme

            if self.is_valid(self.prog[end]):
                if self.prog[end].isalpha():
                    self.logger.log_lexical_error(self.line_no, self.prog[self.ptr:end + 1], 'Invalid number')
                    self.ptr = end + 1
                    return None
                lexeme = self.prog[self.ptr:end]
                token_type = 'NUM'
                self.ptr = end
                return token_type, lexeme
            else:
                self.logger.log_lexical_error(self.line_no, self.prog[self.ptr:end + 1], 'Invalid input')
                self.ptr = end + 1
                return None

        # Symbol DFA
        elif self.prog[self.ptr] in [',', ';', ':', '[', ']', '(', ')', '{', '}', '+', '-', '<']:
            lexeme = self.prog[self.ptr]
            token_type = 'SYMBOL'
            self.ptr += 1
            return token_type, lexeme

        elif self.prog[self.ptr] == '=':
            if not self.is_finished(self.ptr + 1) and self.prog[self.ptr + 1] == '=':
                self.ptr += 2
                return 'SYMBOL', '=='
            elif not self.is_finished(self.ptr + 1) and not self.is_valid(self.prog[self.ptr + 1]):
                self.logger.log_lexical_error(self.line_no, self.prog[self.ptr:self.ptr + 2], 'Invalid input')
                self.ptr += 2
                return None
            else:
                self.ptr += 1
                return 'SYMBOL', '='

        elif self.prog[self.ptr] == '*':
            if not self.is_finished(self.ptr + 1) and self.prog[self.ptr + 1] == '/':
                self.logger.log_lexical_error(self.line_no, '*/', 'Unmatched comment')
                self.ptr = end + 2
                return None
            elif not self.is_finished(self.ptr + 1) and not self.is_valid(self.prog[self.ptr + 1]):
                self.logger.log_lexical_error(self.line_no, self.prog[self.ptr:self.ptr + 2], 'Invalid input')
                self.ptr += 2
                return None
            else:
                self.ptr += 1
                return 'SYMBOL', '*'

        ## comment DFA
        elif self.prog[self.ptr] == '/':
            # // comment
            if not self.is_finished(self.ptr + 1) and self.prog[self.ptr + 1] == '/':
                end = self.ptr + 1
                ## any character even unvalid ones
                while self.prog[end] != '\n':
                    end += 1
                    if self.is_finished(end):
                        self.ptr = end
                        ## no need to return lexeme
                        return 'COMMENT', None

                self.line_no += 1
                self.ptr = end + 1
                return 'COMMENT', None

            # /* */  comment
            elif not self.is_finished(self.ptr + 1) and self.prog[self.ptr + 1] == '*':
                start_line = self.line_no
                end = self.ptr + 2
                while not self.is_finished(end+1):
                    if self.prog[end] == '*' and self.prog[end+1] == '/':
                        self.ptr = end + 2
                        return 'COMMENT', None

                    if self.prog[end] == '\n':
                        self.line_no += 1
                    end+=1
                if len(self.prog) > self.ptr+7:
                    self.logger.log_lexical_error(start_line,  self.prog[self.ptr: self.ptr+7] + "...", 'Unclosed comment')
                else:
                    self.logger.log_lexical_error(start_line,  self.prog[self.ptr: self.ptr+7], 'Unclosed comment')
                self.ptr = end + 1
                return None

            self.logger.log_lexical_error(self.line_no,  self.prog[self.ptr], 'Invalid input')
            self.ptr = end + 1
            return None

        ## Whitespace DFA
        elif self.prog[self.ptr] in [' ', '\n', '\t', '\r', '\f', '\v']:
            lexeme = self.prog[self.ptr]
            if lexeme == '\n':
                self.line_no += 1
            self.ptr += 1
            return 'WHITESPACE', lexeme
        else:
            self.logger.log_lexical_error(self.line_no, self.prog[self.ptr], 'Invalid input')
            self.ptr += 1
            return None


