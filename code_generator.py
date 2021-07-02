from logger import Logger
from symbol_table import SymbolTable


class CodeGenerator:
    def __init__(self, scanner):
        self.scanner = scanner
        self.semantic_errors = []
        self.symbol_table = SymbolTable()
        self.semantic_stack = []
        self.for_while_state = []
        self.PB = []
        self.temp_pointer = 1000 - 4
        self.data_pointer = 500 - 4
        self.i = 0
        self.global_finished = None
        self.main_start = 0
        self.current_scope = None
        self.gen_func = {'ptype': self.ptype,
                         'declare': self.declare,
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
                         'end_call': self.end_call,
                         'finished': self.finished,
                         'type_check': self.type_check}

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

    def pid(self, arg=None):
        address = self.find_address(arg)
        if address is None:
            Logger.get_instance().log_semantic_error(self.scanner.line_no, f"'{arg}' is not defined.")
            address = 0
        self.semantic_stack.append(address)

    def pop(self, arg=None):
        self.semantic_stack.pop()

    def pnum(self, arg=None):
        self.semantic_stack.append('#' + arg)

    def save_array(self, arg=None):
        number = int(self.semantic_stack.pop()[1:])
        self.type_check()
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
        self.operand_check(op1, op2)
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
        self.operand_check(op1, op2)
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
        self.operand_check(op1, op2)
        temp_address = self.get_temp()
        self.PB.append(f'(MULT, {op1}, {op2}, {temp_address})')
        self.i += 1
        self.semantic_stack.append(temp_address)

    def neg(self, arg=None):
        op = self.semantic_stack.pop()
        if self.get_type(op) != 'int':
            Logger.get_instance().log_semantic_error(self.scanner.line_no, f"Type mismatch in operands, Got array instead of int.")
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
        if self.for_while_state:
            self.PB.append(f'(JP, {self.semantic_stack[self.for_while_state[-1]]}, ,)')
            self.i += 1
        else:
            Logger.get_instance().log_semantic_error(self.scanner.line_no, f"No 'while' or 'for' found for 'break'.")

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

    def set_for_count(self, arg=None):
        var_count = self.get_temp()
        self.PB.append(f'(ASSIGN, #{self.semantic_stack[-1]}, {var_count}, )')
        ptr = self.get_temp()
        self.PB.append(f'(ASSIGN, #{self.semantic_stack[-2]}, {ptr}, )')
        self.i += 2
        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.append(var_count)
        self.semantic_stack.append(ptr)

    def parameter(self, arg=None):
        id_address = self.semantic_stack.pop()
        self.symbol_table.add_attr(id_address, self.current_scope, {'kind': 'parameter'})

    def param_array(self, arg=None):
        id_address = self.semantic_stack.pop()
        self.symbol_table.add_attr(id_address, self.current_scope, {'kind': 'param_array', 'length': 0})

    def start_func(self, arg=None):
        if self.global_finished is None:
            self.global_finished = self.i
            self.PB.append('')
            self.i += 1
        address = self.semantic_stack[-1]
        self.current_scope = self.symbol_table.get_id_from_address(address)
        if self.current_scope == 'main':
            self.PB[self.global_finished] = f'(JP, {self.i}, , )'
            self.PB.append('')
            self.main_start = self.i
            self.i += 1
        self.semantic_stack.append('function started')
        return_value = self.get_temp()
        return_address = self.get_temp()
        self.symbol_table.add_attr(address, None,
                                   {'kind': 'func', 'return_value': return_value, 'return_address': return_address})

    def update_func(self, arg=None):
        length = len(self.symbol_table.get_ordered_params(self.current_scope))
        while self.semantic_stack.pop() != 'function started':
            continue
        func_addr = self.semantic_stack.pop()
        self.symbol_table.add_attr(func_addr, None, {'length': length, 'start_address': self.i})

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
            # number matching
            if len(params) != len(args):
                Logger.get_instance().log_semantic_error(self.scanner.line_no, f"Mismatch in numbers of arguments of '{function_name}'.")

            for i in range(min(len(params), len(args))):
                if (isinstance(args[i], int) and args[i] >= 1000) or '#' in str(args[i]) or '@' in str(args[i]):
                    arg_name = ''
                    arg_kind = 'var'
                else:
                    arg_name = self.symbol_table.get_id_from_address(args[i])
                    arg_kind = self.symbol_table.get_attr(arg_name, self.current_scope, 'kind')
                if params[i]['kind'] == 'parameter':
                    if arg_kind not in ['var', 'parameter']:
                        Logger.get_instance().log_semantic_error(self.scanner.line_no, f"Mismatch in type of argument {i + 1} of '{function_name}'. Expected 'int' but got 'array' instead.")
                    self.PB.append(f'(ASSIGN, {args[i]}, {params[i]["address"]}, )')
                else:
                    if arg_kind not in ['array', 'param_array']:
                        Logger.get_instance().log_semantic_error(self.scanner.line_no, f"Mismatch in type of argument {i + 1} of '{function_name}'. Expected 'array' but got 'int' instead.")
                    # self.PB.append(f'(ASSIGN, #{args[i]}, {params[i]["address"]}, )')
                    if arg_name != '':
                        arr_len = self.symbol_table.get_attr(arg_name, self.current_scope, 'length')
                        self.PB.append(f'(ASSIGN, {args[i] + arr_len * 4}, {params[i]["address"]}, )')

                self.i += 1
            start_address = self.symbol_table.get_attr(self.symbol_table.get_id_from_address(function_address), None,
                                                       'start_address')
            return_addr = self.symbol_table.get_attr(function_name, None, 'return_address')
            return_value = self.symbol_table.get_attr(function_name, None, 'return_value')
            self.PB.append(f'(ASSIGN, #{self.i + 2}, {return_addr}, )')
            self.PB.append(f'(JP, {start_address}, , )')
            # store return value in temp and push to stack
            temp_value = self.get_temp()
            self.PB.append(f'(ASSIGN, {return_value}, {temp_value}, )')
            self.semantic_stack.append(temp_value)
            self.i += 3

    def finished(self, arg=None):
        return_addr = self.symbol_table.get_attr('main', None, 'return_address')
        self.PB[self.main_start] = f'(ASSIGN, #{self.i}, {return_addr}, )'

    def type_check(self, arg=None):
        id = self.symbol_table.get_id_from_address(self.semantic_stack[-1])
        t = self.symbol_table.get_attr(id, self.current_scope, 'type')
        if t == 'void':
            Logger.get_instance().log_semantic_error(self.scanner.line_no, f"Illegal type of void for '{id}'")

    def operand_check(self, op1, op2):
        type_op1 = self.get_type(op1)
        type_op2 = self.get_type(op2)
        if type_op1 != type_op2:
            Logger.get_instance().log_semantic_error(self.scanner.line_no, f"Type mismatch in operands, Got array instead of int.")

    def get_type(self, op):
        if isinstance(op, int) and op >= 1000:
            return 'int'
        elif '#' in str(op):
            return 'int'
        elif '@' in str(op):
            return 'int'
        else:
            op_name = self.symbol_table.get_id_from_address(op)
            op_type = self.symbol_table.get_attr(op_name, self.current_scope, 'kind')
            if op_type in ['array', 'param_array']:
                return 'array'
            else:
                return 'int'
