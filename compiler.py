# Compiler Project - Spring 2021
# Mahtab Bigverdi - 96105604
# Shadi Ghasemitaheri - 96105972

from scanner import Scanner, keywords
from logger import Logger
from parser import Parser


class Compiler:

    def __init__(self):
        self.scanner = Scanner()
        self.parser = Parser(self.scanner)
        self.prog = ''
        self.logger = Logger.get_instance()
        self.root = None

    def read_input(self, path):
        with open(path, 'r') as file:
            self.prog = file.read()
            self.scanner.set_prog(self.prog)

    def compile(self, path):
        self.read_input(path)
        self.parser.parse()


if __name__ == '__main__':
    Compiler().compile('PA3_sample_programs/T_new/input.txt')
    # Compiler().compile('input.txt')
