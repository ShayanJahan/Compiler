class SymbolTable:
    def __init__(self):
        self.symbols = list()
        self.start_data = 500
        self.start_temp = 1000
        self.byte_length = 4

    def find_address(self, symbol_name):
        for symbol in self.symbols:
            if symbol[0] == symbol_name:
                return symbol
        self.symbols.append((symbol_name, self.start_data))
        self.start_data += self.byte_length
        return self.symbols[-1]

    def get_temp(self):
        self.start_temp += self.byte_length
        return self.start_temp - self.byte_length

    def make_space(self, value):
        self.start_data += value * self.byte_length
