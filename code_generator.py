from symbol_table import SymbolTable


class CodeGenerator:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.semantic_stack = []
        self.for_while_state = []
        self.PB = []
        self.temp_pointer = 1000 - 4
        self.data_pointer = 500 - 4
        self.i = 0
        self.current_scope = None
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
                         'output': self.output,
                         'break': self.break_loop,
                         'break_save': self.break_save,
                         'init_for': self.init_for,
                         'jpf_for': self.jpf_for,
                         'psave_var': self.psave_var,
                         'save_var': self.save_var,
                         'set_for_count': self.set_for_count,
                         'start_func': self.start_func,
                         'parameter': self.parameter,
                         'param_array': self.param_array,
                         'update_func': self.update_func,
                         'end_func': self.end_func,
                         'return': self.return_func,
                         'start_call': self.start_call,
                         'end_call': self.end_call}

    def code_gen(self, action_symbol, arg=None):
        self.gen_func[action_symbol](arg)

    def find_address(self, input):
        return self.symbol_table.find_address(input, self.current_scope)

    def get_temp(self):
        self.temp_pointer += 4
        return self.temp_pointer

    def ptype(self, arg=None):
        self.semantic_stack.append(arg)

    def get_data(self):
        self.data_pointer += 4
        return self.data_pointer

    def declare(self, arg=None):
        address = self.get_data()
        self.symbol_table.add(arg, self.current_scope,
                              {'address': address, 'type': self.semantic_stack.pop(), 'kind': 'var', 'length': 0})
        self.PB.append(f'(ASSIGN, #0, {address}, )')
        self.i += 1
        self.semantic_stack.append(address)

    def start_func(self, arg=None):
        self.current_scope = self.symbol_table.get_id_from_address(self.semantic_stack[-1])
        self.semantic_stack.append('function started')
        return_value = self.get_temp()
        return_address = self.get_temp()
        self.symbol_table.add_attr(self.semantic_stack[-1], None,
                                   {'kind': 'func', 'return_value': return_value, 'return_address': return_address,
                                    'start_address': self.i})

    def pid(self, arg=None):
        address = self.find_address(arg)
        self.semantic_stack.append(address)
        # elif arg != 'output':

    def pop(self, arg=None):
        self.semantic_stack.pop()

    def pnum(self, arg=None):
        self.semantic_stack.append('#' + arg)

    def save_array(self, arg=None):
        number = int(self.semantic_stack.pop()[1:])
        id_address = self.semantic_stack.pop()
        self.symbol_table.add_attr(id_address, self.current_scope, {'kind': 'array', 'length': number})
        for i in range(number - 1):
            address = self.get_data()
            self.PB.append(f'(ASSIGN, #0, {address}, )')
            self.i += 1

        address = self.get_data()
        self.PB.append(f'(ASSIGN, #{id_address}, {address}, )')
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
        self.PB[self.semantic_stack.pop()] = f'(JP, {self.i}, , )'
        self.for_while_state.pop()

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
        length = self.symbol_table.get_attr(self.symbol_table.get_id_from_address(id), self.current_scope, 'length')
        self.PB.append(f'(MULT, {index}, #4, {temp_address})')
        self.PB.append(f'(ADD, {id + length * 4}, {temp_address}, {temp_address})')
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
        self.PB.append(f'(PRINT, {arg}, , )')
        self.i += 1
        self.semantic_stack.append(None)

    # phase 4

    def break_loop(self, arg=None):
        self.PB.append(f'(JP, {self.semantic_stack[self.for_while_state[-1]]}, ,)')
        self.i += 1

    def break_save(self, arg=None):
        self.PB.append(f'(JP, {self.i + 2}, , )')
        self.i += 1
        self.save()
        self.for_while_state.append(len(self.semantic_stack) - 1)

    def init_for(self, arg=None):
        self.PB.append(f'(ASSIGN, @{self.semantic_stack[-2]}, {self.semantic_stack[-4]}, )')
        self.PB.append(f'(ASSIGN, @{self.semantic_stack[-4]}, {self.semantic_stack[-4]}, )')
        self.i += 2

    def jpf_for(self, arg=None):  # pop 5, fill break_save
        self.PB.append(f'(ADD, {self.semantic_stack[-2]}, #4, {self.semantic_stack[-2]})')
        self.PB.append(f'(SUB, {self.semantic_stack[-3]}, #1, {self.semantic_stack[-3]})')
        t = self.get_temp()
        self.PB.append(f'(EQ, {self.semantic_stack[-3]}, #0, {t})')
        self.PB.append(f'(JPF, {t}, {self.semantic_stack[-1]}, )')
        self.i += 4
        self.PB[self.semantic_stack[-5]] = f'(JP, {self.i}, , )'
        self.semantic_stack = self.semantic_stack[:-5]
        self.for_while_state.pop()

    def psave_var(self, arg=None):
        t = self.get_temp()
        self.PB.append(f'(ASSIGN, #{self.semantic_stack[-1]}, {t}, )')
        self.i += 1
        self.semantic_stack.pop()
        self.semantic_stack.append(t)
        self.semantic_stack.append(1)

    def save_var(self, arg=None):
        t = self.get_temp()
        self.PB.append(f'(ASSIGN, #{self.semantic_stack[-1]}, {t}, )')
        self.i += 1
        var_count = self.semantic_stack[-2] + 1
        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.append(var_count)
        print('####', self.semantic_stack)

    def set_for_count(self, arg=None):
        var_count = self.get_temp()
        self.PB.append(f'(ASSIGN, #{self.semantic_stack[-1]}, {var_count}, )')
        ptr = self.get_temp()
        print(self.semantic_stack)
        self.PB.append(f'(ASSIGN, #{self.semantic_stack[-2]}, {ptr}, )')
        self.i += 2
        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.append(var_count)
        self.semantic_stack.append(ptr)

    def parameter(self, arg=None):
        id_address = self.semantic_stack.pop()
        self.symbol_table.add_attr(id_address, self.current_scope, {'kind': 'param'})

    def param_array(self, arg=None):
        id_address = self.semantic_stack.pop()
        self.symbol_table.add_attr(id_address, self.current_scope, {'kind': 'param_array', 'length': 0})

    def update_func(self, arg=None):
        length = len(self.symbol_table.get_ordered_params(self.current_scope))
        while self.semantic_stack.pop() != 'function started':
            continue
        func_addr = self.semantic_stack.pop()
        self.symbol_table.add_attr(func_addr, None, {'length': length})

    def end_func(self, arg=None):
        return_value = self.symbol_table.get_attr(self.current_scope, None, 'return_value')
        return_addr = self.symbol_table.get_attr(self.current_scope, None, 'return_address')
        self.PB.append(f'(ASSIGN, #0, {return_value}, )')
        self.PB.append(f'(JP, @{return_addr}, , )')
        self.i += 2
        self.current_scope = None

    def return_func(self, arg=None):
        return_value = self.symbol_table.get_attr(self.current_scope, None, 'return_value')
        return_addr = self.symbol_table.get_attr(self.current_scope, None, 'return_address')
        value = self.semantic_stack.pop()
        self.PB.append(f'(ASSIGN, {value}, {return_value}, )')
        self.PB.append(f'(JP, @{return_addr}, , )')
        self.i += 2

    def start_call(self, arg=None):
        self.semantic_stack.append('call started')

    def end_call(self, arg=None):
        args = []
        while True:
            top = self.semantic_stack.pop()
            if top == 'call started':
                break
            args.append(top)
        args = args[::-1]
        function_address = self.semantic_stack.pop()
        function_name = self.symbol_table.get_id_from_address(function_address)
        if function_name == 'output':
            self.output(args[0])
        else:
            params = self.symbol_table.get_ordered_params(self.symbol_table.get_id_from_address(function_address))
            for i in range(len(params)):
                if params[i]['kind'] == 'parameter':
                    self.PB.append(f'(ASSIGN, {args[i]}, {params[i]["address"]}, )')
                else:
                    self.PB.append(f'(ASSIGN, #{args[i]}, {params[i]["address"]}, )')
                self.i += 1
            start_address = self.symbol_table.get_attr(self.symbol_table.get_id_from_address(function_address), None,
                                                       'start_address')
            self.PB.append(f'(JP, {start_address}, , )')
            self.i += 1
