class SymbolTable():
    def __init__(self):
        self.symbol_dict = {('output', None): {'address' : 0, 'kind': 'func'}}

    def add(self, input, current_scope, dictionary):
        self.symbol_dict[(input, current_scope)] = dictionary

    def find_address(self, input, current_scope):
        return self.get_attr(input, current_scope, 'address')

    def get_id_from_address(self, id_address):
        return next((key for key, val in self.symbol_dict.items() if val['address'] == id_address), None)[0]

    def add_attr(self, id_adress, current_scope, dict_attr):
        self.symbol_dict[(self.get_id_from_address(id_adress), current_scope)].update(dict_attr)

    def get_ordered_params(self, function_name):
        params = []
        for k, v in self.symbol_dict.items():
            if k[1] == function_name and v['kind'] in ['parameter', 'param_array']:
                params.append(v)
        return params

    def get_attr(self, input, current_scope, attr):
        if (input, current_scope) in self.symbol_dict:
            return self.symbol_dict[(input, current_scope)][attr]
        elif (input, None) in self.symbol_dict:
            return self.symbol_dict[(input, None)][attr]
        else:
            raise ValueError('not found')
            # return None


