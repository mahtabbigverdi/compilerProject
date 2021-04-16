from logger import Logger
from predict_sets import first, follow
from anytree import Node
import traceback

class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.token = None

    def parse(self):
        self.token = self.scanner.get_next_token()
        return self.program()

    def lookahead(self):
        if self.token[0] in ['ID', 'NUM']:
            return self.token[0]
        return self.token[1]

    def match(self, expected_token, parent):
        if self.lookahead() == expected_token:
            node = Node('$', parent=parent) if expected_token == '$' else Node('(%s, %s) ' % self.token, parent=parent)
            self.token = self.scanner.get_next_token()
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing {expected_token}')

    def program(self):
        root = None
        if self.lookahead() in first['Program']:
            root = Node('Program')
            self.declaration_list(root)
            self.match('$', root)  # TODO
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
        return root

    def declaration_list(self, parent):
        if self.lookahead() in first['Declaration']:
            node = Node('Declaration-list', parent=parent)
            self.declaration(node)
            self.declaration_list(node)
        elif self.lookahead() in follow['Declaration-list']:
            node = Node('Declaration-list', parent=parent)
            child = Node('epsilon', parent=node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.declaration_list(parent)

    def declaration(self, parent):
        if self.lookahead() in first['Declaration-initial']:
            node = Node('Declaration', parent=parent)
            self.declaration_initial(node)
            self.declaration_prime(node)
        elif self.lookahead() in follow['Declaration']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Declaration')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.declaration(parent)

    def declaration_initial(self, parent):
        if self.lookahead() in first['Type-specifier']:
            node = Node('Declaration-initial', parent=parent)
            self.type_specifier(node)
            self.match('ID', node)
        elif self.lookahead() in follow['Declaration-initial']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Declaration-initial')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.declaration_initial(parent)

    def declaration_prime(self, parent):
        if self.lookahead() in first['Fun-declaration-prime']:
            node = Node('Declaration-prime', parent=parent)
            self.fun_declaration_prime(node)
        elif self.lookahead() in first['Var-declaration-prime']:
            node = Node('Declaration-prime', parent=parent)
            self.var_declaration_prime(node)
        elif self.lookahead() in follow['Declaration-prime']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Declaration-prime')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.declaration_prime(parent)

    def var_declaration_prime(self, parent):
        if self.lookahead() == ';':
            node = Node('Var-declaration-prime', parent=parent)
            self.match(';', node)
        elif self.lookahead() == '[':
            node = Node('Var-declaration-prime', parent=parent)
            self.match('[', node)
            self.match('NUM', node)
            self.match(']', node)
        elif self.lookahead() in follow['Var-declaration-prime']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Var-declaration-prime')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.var_declaration_prime(parent)

    def fun_declaration_prime(self, parent):
        if self.lookahead() == '(':
            node = Node('Fun-declaration-prime', parent=parent)
            self.match('(', node)
            self.params(node)
            self.match(')', node)
            self.compound_stmt(node)
        elif self.lookahead() in follow['Fun-declaration-prime']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Fun-declaration-prime')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.fun_declaration_prime(parent)

    def type_specifier(self, parent):
        if self.lookahead() == 'int':
            node = Node('Type-specifier', parent=parent)
            self.match('int', node)
        elif self.lookahead() == 'void':
            node = Node('Type-specifier', parent=parent)
            self.match('void', node)
        elif self.lookahead() in follow['Type-specifier']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Type-specifier')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.type_specifier(parent)

    def params(self, parent):
        if self.lookahead() == 'int':
            node = Node('Params', parent=parent)
            self.match('int', node)
            self.match('ID', node)
            self.param_prime(node)
            self.param_list(node)
        elif self.lookahead() == 'void':
            node = Node('Params', parent=parent)
            self.match('void', node)
            self.param_list_void_abtar(node)
        elif self.lookahead() in follow['Params']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Params')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.params(parent)

    def param_list_void_abtar(self, parent):
        if self.lookahead() == 'ID':
            node = Node('Param-list-void-abtar', parent=parent)
            self.match('ID', node)
            self.param_prime(node)
            self.param_list(node)
        elif self.lookahead() in follow['Param-list-void-abtar']:
            node = Node('Param-list-void-abtar', parent=parent)
            child = Node('epsilon', parent=node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.param_list_void_abtar(parent)

    def param_list(self, parent):
        if self.lookahead() == ',':
            node = Node('Param-list', parent=parent)
            self.match(',', node)
            self.param(node)
            self.param_list(node)
        elif self.lookahead() in follow['Param-list']:
            node = Node('Param-list', parent=parent)
            child = Node('epsilon', parent=node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.param_list(parent)

    def param(self, parent):
        if self.lookahead() == first['Declaration-initial']:
            node = Node('Param', parent=parent)
            self.declaration_initial(node)
            self.param_prime(node)
        elif self.lookahead() in follow['Param']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Param')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.param(parent)

    def param_prime(self, parent):
        if self.lookahead() == '[':
            node = Node('Param-prime', parent=parent)
            self.match('[', node)
            self.match(']', node)
        elif self.lookahead() in follow['Param-prime']:
            node = Node('Param-prime', parent=parent)
            child = Node('epsilon', parent=node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.param_prime(parent)

    def compound_stmt(self, parent):
        if self.lookahead() == '{':
            node = Node('Compound-stmt', parent=parent)
            self.match('{', node)
            self.declaration_list(node)
            self.statement_list(node)
            self.match('}', node)
        elif self.lookahead() in follow['Compound-stmt']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Compound-stmt')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.compound_stmt(parent)

    def statement_list(self, parent):
        if self.lookahead() in first['Statement']:
            node = Node('Statement-list', parent=parent)
            self.statement(node)
            self.statement_list(node)
        elif self.lookahead() in follow['Statement-list']:
            node = Node('Statement-list', parent=parent)
            child = Node('epsilon', parent=node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.statement_list(parent)

    def statement(self, parent):
        if self.lookahead() in first['Expression-stmt']:
            node = Node('Statement', parent=parent)
            self.expression_stmt(node)
        elif self.lookahead() in first['Compound-stmt']:
            node = Node('Statement', parent=parent)
            self.compound_stmt(node)
        elif self.lookahead() in first['Selection-stmt']:
            node = Node('Statement', parent=parent)
            self.selection_stmt(node)
        elif self.lookahead() in first['Iteration-stmt']:
            node = Node('Statement', parent=parent)
            self.iteration_stmt(node)
        elif self.lookahead() in first['Return-stmt']:
            node = Node('Statement', parent=parent)
            self.return_stmt(node)
        elif self.lookahead() in first['For-stmt']:
            node = Node('Statement', parent=parent)
            self.for_stmt(node)
        elif self.lookahead() in follow['Statement']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Statement')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.statement(parent)

    def expression_stmt(self, parent):
        if self.lookahead() in first['Expression']:
            node = Node('Expression-stmt', parent=parent)
            self.expression(node)
            self.match(';', node)
        elif self.lookahead() == 'break':
            node = Node('Expression-stmt', parent=parent)
            self.match('break', node)
            self.match(';', node)
        elif self.lookahead() == ';':
            node = Node('Expression-stmt', parent=parent)
            self.match(';', node)
        elif self.lookahead() in follow['Expression-stmt']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Expression-stmt')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.expression_stmt(parent)

    def selection_stmt(self, parent):
        if self.lookahead() == 'if':
            node = Node('Selection-stmt', parent=parent)
            self.match('if', node)
            self.match('(', node)
            self.expression(node)
            self.match(')', node)
            self.statement(node)
            self.match('else', node)
            self.statement(node)
        elif self.lookahead() in follow['Selection-stmt']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Selection-stmt')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.selection_stmt(parent)

    def iteration_stmt(self, parent):
        if self.lookahead() == 'while':
            node = Node('Iteration-stmt', parent=parent)
            self.match('while', node)
            self.match('(', node)
            self.expression(node)
            self.match(')', node)
            self.statement(node)
        elif self.lookahead() in follow['Iteration-stmt']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Iteration-stmt')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.iteration_stmt(parent)

    def return_stmt(self, parent):
        if self.lookahead() == 'return':
            node = Node('Return-stmt', parent=parent)
            self.match('return', node)
            self.return_stmt_prime(node)
        elif self.lookahead() in follow['Return-stmt']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Return-stmt')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.return_stmt(parent)

    def return_stmt_prime(self, parent):
        if self.lookahead() == ';':
            node = Node('Return-stmt-prime', parent=parent)
            self.match(';', node)
        elif self.lookahead() in first['Expression']:
            node = Node('Return-stmt-prime', parent=parent)
            self.expression(node)
            self.match(';', node)
        elif self.lookahead() in follow['Return-stmt-prime']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Return-stmt-prime')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.return_stmt_prime(parent)

    def for_stmt(self, parent):
        if self.lookahead() == 'for':
            node = Node('For-stmt', parent=parent)
            self.match('for', node)
            self.match('ID', node)
            self.match('=', node)
            self.vars(node)
            self.statement(node)
        elif self.lookahead() in follow['For-stmt']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing For-stmt')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.for_stmt(parent)

    def vars(self, parent):
        if self.lookahead() in first['Var']:
            node = Node('Vars', parent=parent)
            self.var(node)
            self.var_zegond(node)
        elif self.lookahead() in follow['Vars']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Vars')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.vars(parent)

    def var_zegond(self, parent):
        if self.lookahead() == ',':
            node = Node('Var-zegond', parent=parent)
            self.match(',', node)
            self.var(node)
            self.var_zegond(node)
        elif self.lookahead() in follow['Var-zegond']:
            node = Node('Var-zegond', parent=parent)
            child = Node('epsilon', parent=node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.var_zegond(parent)

    def var(self, parent):
        if self.lookahead() == 'ID':
            node = Node('Var', parent=parent)
            self.match('ID', node)
            self.var_prime(node)
        elif self.lookahead() in follow['Var']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Var')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.var(parent)

    def expression(self, parent):
        if self.lookahead() in first['Simple-expression-zegond']:
            node = Node('Expression', parent=parent)
            self.simple_expression_zegond(node)
        elif self.lookahead() == 'ID':
            node = Node('Expression', parent=parent)
            self.match('ID', node)
            self.b(node)
        elif self.lookahead() in follow['Expression']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Expression')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.expression(parent)

    def b(self, parent):
        if self.lookahead() == '=':
            node = Node('B', parent=parent)
            self.match('=', node)
            self.expression(node)
        elif self.lookahead() == '[':
            node = Node('B', parent=parent)
            self.match('[', node)
            self.expression(node)
            self.match(']', node)
            self.h(node)
        elif self.lookahead() in first['Simple-expression-prime'] or self.lookahead() in follow['B']:
            node = Node('B', parent=parent)
            self.simple_expression_prime(node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.b(parent)

    def h(self, parent):
        if self.lookahead() == '=':
            node = Node('H', parent=parent)
            self.match('=',  node)
            self.expression(node)
        elif self.lookahead() in first['G'] or self.lookahead() in first['D'] \
                or self.lookahead() in first['C'] or self.lookahead() in follow['H']:
            node = Node('H', parent=parent)
            self.g(node)
            self.d(node)
            self.c(node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.h(parent)

    def simple_expression_zegond(self, parent):
        if self.lookahead() in first['Additive-expression-zegond']:
            node = Node('Simple-expression-zegond', parent=parent)
            self.additive_expression_zegond(node)
            self.c(node)
        elif self.lookahead() in follow['Simple-expression-zegond']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Simple-expression-zegond')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.simple_expression_zegond(parent)

    def simple_expression_prime(self, parent):
        if self.lookahead() in first['Additive-expression-prime'] or self.lookahead() in first['C'] or\
                self.lookahead() in follow['Simple-expression-prime']:
            node = Node('Simple-expression-prime', parent=parent)
            self.additive_expression_prime(node)
            self.c(node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.simple_expression_prime(parent)

    def c(self, parent):
        if self.lookahead() in first['Relop']:
            node = Node('C', parent=parent)
            self.relop(node)
            self.additive_expression(node)
        elif self.lookahead() in follow['C']:
            node = Node('C', parent=parent)
            child = Node('epsilon', parent=node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.c(parent)

    def relop(self, parent):
        if self.lookahead() == '<':
            node = Node('Relop', parent=parent)
            self.match('<', node)
        elif self.lookahead() == '==':
            node = Node('Relop', parent=parent)
            self.match('==', node)
        elif self.lookahead() in follow['Relop']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Relop')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.relop(parent)

    def additive_expression(self, parent):
        if self.lookahead() in first['Term']:
            node = Node('Additive-expression', parent=parent)
            self.term(node)
            self.d(node)
        elif self.lookahead() in follow['Additive-expression']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Additive-expression')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.additive_expression(parent)

    def additive_expression_prime(self, parent):
        if self.lookahead() in first['Term-prime'] or self.lookahead() in first['D'] or\
                self.lookahead() in follow['Additive-expression-prime']:
            node = Node('Additive-expression-prime', parent=parent)
            self.term_prime(node)
            self.d(node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.additive_expression_prime(parent)

    def additive_expression_zegond(self, parent):
        if self.lookahead() in first['Term-zegond']:
            node = Node('Additive-expression-zegond', parent=parent)
            self.term_zegond(node)
            self.d(node)
        elif self.lookahead() in follow['Additive-expression-zegond']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Additive-expression-zegond')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.additive_expression_zegond(parent)

    def d(self, parent):
        if self.lookahead() in first['Addop']:
            node = Node('D', parent=parent)
            self.addop(node)
            self.term(node)
            self.d(node)
        elif self.lookahead() in follow['D']:
            node = Node('D', parent=parent)
            child = Node('epsilon', parent=node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.d(parent)

    def addop(self, parent):
        if self.lookahead() == '+':
            node = Node('Addop', parent=parent)
            self.match('+', node)
        elif self.lookahead() == '-':
            node = Node('Addop', parent=parent)
            self.match('-', node)
        elif self.lookahead() in follow['Addop']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Addop')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.addop(parent)

    def term(self, parent):
        if self.lookahead() in first['Signed-factor']:
            node = Node('Term', parent=parent)
            self.signed_factor(node)
            self.g(node)
        elif self.lookahead() in follow['Term']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Term')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.term(parent)

    def term_prime(self, parent):
        if self.lookahead() in first['Signed-factor-prime'] or self.lookahead() in first['G'] or\
                self.lookahead() in follow['Term-prime']:
            node = Node('Term-prime', parent=parent)
            self.signed_factor_prime(node)
            self.g(node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.term_prime(parent)

    def term_zegond(self, parent):
        if self.lookahead() in first['Signed-factor-zegond']:
            node = Node('Term-zegond', parent=parent)
            self.signed_factor_zegond(node)
            self.g(node)
        elif self.lookahead() in follow['Term-zegond']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Term-zegond')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.term_zegond(parent)

    def g(self, parent):
        if self.lookahead() == '*':
            node = Node('G', parent=parent)
            self.match('*', node)
            self.signed_factor(node)
            self.g(node)
        elif self.lookahead() in follow['G']:
            node = Node('G', parent=parent)
            child = Node('epsilon', parent=node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.g(parent)

    def signed_factor(self, parent):
        if self.lookahead() == '+':
            node = Node('Signed-factor', parent=parent)
            self.match('+', node)
            self.factor(node)
        elif self.lookahead() == '-':
            node = Node('Signed-factor', parent=parent)
            self.match('-', node)
            self.factor(node)
        elif self.lookahead() in first['Factor']:
            node = Node('Signed-factor', parent=parent)
            self.factor(node)
        elif self.lookahead() in follow['Signed-factor']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Signed-factor')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.signed_factor(parent)

    def signed_factor_prime(self, parent):
        if self.lookahead() in first['Factor-prime'] or self.lookahead() in follow['Signed-factor-prime']:
            node = Node('Signed-factor-prime', parent=parent)
            self.factor_prime(node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.signed_factor_prime(parent)

    def signed_factor_zegond(self, parent):
        if self.lookahead() == '+':
            node = Node('Signed-factor-zegond', parent=parent)
            self.match('+', node)
            self.factor(node)
        elif self.lookahead() == '-':
            node = Node('Signed-factor-zegond', parent=parent)
            self.match('-', node)
            self.factor(node)
        elif self.lookahead() in first['Factor-zegond']:
            node = Node('Signed-factor-zegond', parent=parent)
            self.factor_zegond(node)
        elif self.lookahead() in follow['Signed-factor-zegond']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Signed-factor-zegond')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.signed_factor_zegond(parent)

    def factor(self, parent):
        if self.lookahead() == '(':
            node = Node('Factor', parent=parent)
            self.match('(', node)
            self.expression(node)
            self.match(')', node)
        elif self.lookahead() == 'ID':
            node = Node('Factor', parent=parent)
            self.match('ID', node)
            self.var_call_prime(node)
        elif self.lookahead() == 'NUM':
            node = Node('Factor', parent=parent)
            self.match('NUM', node)
        elif self.lookahead() in follow['Factor']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Factor')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.factor(parent)

    def var_call_prime(self, parent):
        if self.lookahead() == '(':
            node = Node('Var-call-prime', parent=parent)
            self.match('(', node)
            self.args(node)
            self.match(')', node)
        elif self.lookahead() in first['Var-prime'] or self.lookahead() in follow['Var-call-prime']:
            node = Node('Var-call-prime', parent=parent)
            self.var_prime(node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.var_call_prime(parent)

    def var_prime(self, parent):
        if self.lookahead() == '[':
            node = Node('Var-prime', parent=parent)
            self.match('[', node)
            self.expression(node)
            self.match(']', node)
        elif self.lookahead() in follow['Var-prime']:
            node = Node('Var-prime', parent=parent)
            child = Node('epsilon', parent=node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.var_prime(parent)

    def factor_prime(self, parent):
        if self.lookahead() == '(':
            node = Node('Factor-prime', parent=parent)
            self.match('(', node)
            self.args(node)
            self.match(')', node)
        elif self.lookahead() in follow['Factor-prime']:
            node = Node('Factor-prime', parent=parent)
            child = Node('epsilon', parent=node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.factor_prime(parent)

    def factor_zegond(self, parent):
        if self.lookahead() == '(':
            node = Node('Factor-zegond', parent=parent)
            self.match('(', node)
            self.expression(node)
            self.match(')', node)
        elif self.lookahead() == 'NUM':
            node = Node('Factor-zegond', parent=parent)
            self.match('NUM', node)
        elif self.lookahead() in follow['Factor-zegond']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Factor-zegond')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.factor_zegond(parent)

    def args(self, parent):
        if self.lookahead() in first['Arg-list']:
            node = Node('Args', parent=parent)
            self.arg_list(node)
        elif self.lookahead() in follow['Args']:
            node = Node('Args', parent=parent)
            child = Node('epsilon', parent=node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.args(parent)

    def arg_list(self, parent):
        if self.lookahead() in first['Expression']:
            node = Node('Arg-list', parent=parent)
            self.expression(node)
            self.arg_list_prime(node)
        elif self.lookahead() in follow['Arg-list']:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'missing Arg-list')
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.arg_list(parent)

    def arg_list_prime(self, parent):
        if self.lookahead() == ',':
            node = Node('Arg-list-prime', parent=parent)
            self.match(',', node)
            self.expression(node)
            self.arg_list_prime(node)
        elif self.lookahead() in follow['Arg-list-prime']:
            node = Node('Arg-list-prime', parent=parent)
            child = Node('epsilon', parent=node)
        else:
            Logger.get_instance().log_syntax_error(self.scanner.line_no, f'illegal {self.lookahead()}')
            self.token = self.scanner.get_next_token()
            self.arg_list_prime(parent)
