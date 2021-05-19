class CodeGenerator:
    def __init__(self):
        self.symbol_table = {}
        self.semantic_stack = []
        self.PB = []
        self.temp_pointer = 1000 - 4
        self.data_pointer = 500 - 4
        self.i = 0
        self.gen_func = {'ptype': self.ptype,
                         'pid': self.pid,
                         'pop': self.pop,
                         'pnum': self.pnum,
                         'save_array': self.save_array,
                         'save': self.save,
                         'jpf_save': self.jpf_save,
                         'jp': self.jp,
                         'label': self.label,
                         'while': self.iter,
                         'assign': self.assign,
                         'array_index': self.array_index,
                         'poperator': self.poperator,
                         'relop': self.relop,
                         'addop': self.addop,
                         'mult': self.mult,
                         'neg': self.neg,
                         'output': self.output}

    def code_gen(self, action_symbol, arg=None):
        self.gen_func[action_symbol](arg)

    def find_address(self, input):
        return self.symbol_table[input]['address']

    def get_temp(self):
        self.temp_pointer += 4
        return self.temp_pointer

    def ptype(self, arg=None):
        self.semantic_stack.append(arg)

    def get_data(self):
        self.data_pointer += 4
        return self.data_pointer

    def pid(self, arg=None):
        if arg in self.symbol_table:
            address = self.find_address(arg)
            self.semantic_stack.append(address)
        elif arg != 'output':
            address = self.get_data()
            self.symbol_table[arg] = {'address': address, 'type': self.semantic_stack.pop(), 'length': 0}
            self.PB.append(f'(ASSIGN, #0, {address}, )')
            self.i += 1
            self.semantic_stack.append(address)

    def pop(self, arg=None):
        self.semantic_stack.pop()

    def pnum(self, arg=None):
        self.semantic_stack.append('#' + arg)

    def save_array(self, arg=None):
        number = int(self.semantic_stack.pop()[1:])
        id_address = self.semantic_stack.pop()
        # id = next((key for key, val in self.symbol_table.items() if val['address'] == id_address), None)
        # self.symbol_table[id]['length'] = number
        for i in range(number - 1):
            address = self.get_data()
            self.PB.append(f'(ASSIGN, #0, {address}, )')
            self.i += 1

    def save(self, arg=None):
        self.semantic_stack.append(self.i)
        self.PB.append('')
        self.i += 1

    def jpf_save(self, arg=None):
        index = self.semantic_stack.pop()
        self.PB[index] = f'(JPF, {self.semantic_stack.pop()}, {self.i + 1}, )'
        self.semantic_stack.append(self.i)
        self.i += 1
        self.PB.append('')

    def jp(self, arg=None):
        self.PB[self.semantic_stack.pop()] = f'(JP, {self.i}, , )'

    def label(self, arg=None):
        self.semantic_stack.append(self.i)

    def iter(self, arg=None):
        index = self.semantic_stack.pop()
        self.PB[index] = f'(JPF, {self.semantic_stack.pop()}, {self.i + 1}, )'
        self.PB.append(f'(JP, {self.semantic_stack.pop()}, , )')
        self.i += 1

    def assign(self, arg=None):
        rhs = self.semantic_stack.pop()
        lhs = self.semantic_stack.pop()
        self.PB.append(f'(ASSIGN, {rhs}, {lhs}, )')
        self.i += 1
        self.semantic_stack.append(lhs)

    def array_index(self, arg=None):
        temp_address = self.get_temp()
        index = self.semantic_stack.pop()
        id = self.semantic_stack.pop()
        self.PB.append(f'(MULT, {index}, #4, {temp_address})')
        self.PB.append(f'(ADD, #{id}, {temp_address}, {temp_address})')
        self.semantic_stack.append('@' + str(temp_address))
        self.i += 2

    def poperator(self, arg=None):
        self.semantic_stack.append(arg)

    def relop(self, arg=None):
        op2 = self.semantic_stack.pop()
        operator = self.semantic_stack.pop()
        op1 = self.semantic_stack.pop()

        temp_address = self.get_temp()
        if operator == '<':
            self.PB.append(f'(LT, {op1}, {op2}, {temp_address})')
        elif operator == '==':
            self.PB.append(f'(EQ, {op1}, {op2}, {temp_address})')
        self.i += 1
        self.semantic_stack.append(temp_address)

    def addop(self, arg=None):
        op2 = self.semantic_stack.pop()
        operator = self.semantic_stack.pop()
        op1 = self.semantic_stack.pop()

        temp_address = self.get_temp()
        if operator == '+':
            self.PB.append(f'(ADD, {op1}, {op2}, {temp_address})')
        elif operator == '-':
            self.PB.append(f'(SUB, {op1}, {op2}, {temp_address})')
        self.i += 1
        self.semantic_stack.append(temp_address)

    def mult(self, arg=None):
        op2 = self.semantic_stack.pop()
        op1 = self.semantic_stack.pop()

        temp_address = self.get_temp()
        self.PB.append(f'(MULT, {op1}, {op2}, {temp_address})')
        self.i += 1
        self.semantic_stack.append(temp_address)

    def neg(self, arg=None):
        op = self.semantic_stack.pop()
        temp_address = self.get_temp()
        self.PB.append(f'(SUB, #0, {op}, {temp_address})')
        self.i += 1
        self.semantic_stack.append(temp_address)

    def output(self, arg=None):
        id = self.semantic_stack.pop()
        self.PB.append(f'(PRINT, {id}, , )')
        self.i += 1
        self.semantic_stack.append(None)
