# Compiler Project - Spring 2021
# Mahtab Bigverdi - 96105604
# Shadi Ghasemitaheri - 96105972

from scanner import Scanner, keywords
from logger import Logger
from parser import Parser


class Compiler:

    def __init__(self):
        self.symbol_table = keywords.copy()
        self.scanner = Scanner(self.symbol_table)
        self.parser = Parser(self.scanner)
        self.prog = ''
        self.logger = Logger.get_instance()

    def read_input(self, path):
        with open(path, 'r') as file:
            self.prog = file.read()
            self.scanner.set_prog(self.prog)

    def compile(self, path):
        self.read_input(path)
        root = self.parser.parse()

        self.logger.save_lexical_errors()
        self.logger.save_symbol_table(self.symbol_table)
        self.logger.save_parse_tree(root)
        self.logger.save_syntax_errors()

        # while True:
        #     token = self.scanner.get_next_token()
        #     if token[0] == '$':
        #         print('Compiled Successfully!')
        #         break
        #     self.logger.add_token(self.scanner.line_no, *token)
        # self.logger.save_tokens()


if __name__ == '__main__':
    Compiler().compile('PA2_sample_programs/T1/input.txt')
    # Compiler().compile('input.txt')
