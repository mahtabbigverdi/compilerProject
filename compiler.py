# Compiler Project - Spring 2021
# Mahtab Bigverdi - 96105604
# Shadi Ghasemitaheri - 96105972

from scanner import Scanner


class Compiler:

    def __init__(self):
        self.symbol_table = {}
        self.scanner = Scanner(self.symbol_table)
        self.prog = ''
        self.prog_len = 0

    def read_input(self, path):
        with open(path, 'r') as file:
            self.prog = file.read()
            self.prog_len = len(self.prog)
            self.scanner.set_prog(self.prog)

    def compile(self, path):
        self.read_input(path)
        while self.prog_len != self.scanner.ptr:
            _ = self.scanner.get_next_token()
        print(f'{path} compiled successfully!')


if __name__ == '__main__':
    Compiler().compile('PA1_sample_programs/T01/input.txt')
