class Symbol:
    def __init__(self, name, variable_type, address_type, address, scope, symbol_type, arguments_count=0):
        self.name = name
        self.variable_type = variable_type
        self.address_type = address_type
        self.address = address
        self.scope = scope
        self.symbol_type = symbol_type
        self.arguments_count = arguments_count


class SymbolTable:
    def __init__(self):
        self.symbols = list()
        self.st_pointer = 100
        self.start_temp = 3000
        self.start_data = 20000
        self.byte_length = 4
        self.return_address = 10

    def find_address(self, symbol_name):
        for symbol in self.symbols:
            if symbol.name == symbol_name:
                return symbol
        return None

    def get_temp(self):
        self.start_temp += self.byte_length
        return self.start_temp - self.byte_length

    def delete_scope(self, scope):
        for symbol in self.symbols:
            if symbol.scope == scope:
                self.symbols.remove(symbol)

    def get_global(self):
        self.start_data += self.byte_length
        return self.start_data - self.byte_length

    def make_space(self, value):
        self.start_data += int(value) * self.byte_length
        return self.start_data - int(value) * self.byte_length

    def add_symbol(self, symbol):
        self.symbols.append(symbol)
