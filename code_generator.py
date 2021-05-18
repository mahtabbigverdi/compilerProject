class CodeGenerator:
    def __init__(self):
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

    def ptype(self, arg=None):
        pass

    def pid(self, arg=None):
        pass

    def pop(self, arg=None):
        pass

    def pnum(self, arg=None):
        pass

    def save_array(self, arg=None):
        pass

    def save(self, arg=None):
        pass

    def jpf_save(self, arg=None):
        pass

    def jp(self, arg=None):
        pass

    def label(self, arg=None):
        pass

    def iter(self, arg=None):
        pass

    def assign(self, arg=None):
        pass

    def array_index(self, arg=None):
        pass

    def poperator(self, arg=None):
        pass

    def relop(self, arg=None):
        pass

    def addop(self, arg=None):
        pass

    def mult(self, arg=None):
        pass

    def neg(self, arg=None):
        pass

    def output(self, arg=None):
        pass
