from SymbolTable import SymbolTable


class Subroutines:
    def __init__(self):
        self.semantic_stack = []
        self.stack = list()
        self.symbol_table = SymbolTable()
        self.program_block = list()
        self.program_block_counter = 0

    def add_to_program_block(self, code, line=None):
        if line is None:
            self.program_block.append(code)
            self.program_block_counter += 1
        else:
            self.program_block[line] = code

    def push_number(self, string):
        temp = self.symbol_table.get_temp()
        value = int(string)
        self.add_to_program_block(f"(ASSIGN, #{value}, {temp}, )")
        self.semantic_stack.append(temp)

    def pop_number(self, string):
        self.semantic_stack.pop()

    def push_id(self, string):
        self.semantic_stack.append(self.symbol_table.find_address(string)[1])

    def define_variable(self, string):
        self.symbol_table.find_address(string)

    def array_space(self, string):
        self.symbol_table.make_space(int(string))

    def save_address(self, string):
        self.semantic_stack.append(self.program_block_counter)
        self.add_to_program_block(code=None)

    def false_condition_jump(self, string):
        compare_result = self.semantic_stack[-2]
        jump_line = self.semantic_stack[-1]

        self.semantic_stack.pop()
        self.semantic_stack.pop()

        self.semantic_stack.append(self.program_block_counter)

        self.add_to_program_block(code=None)
        self.add_to_program_block(code=f"(JPF, {compare_result}, {self.program_block_counter}, )", line=jump_line)

    def jump(self, string):
        jump_line = self.semantic_stack[-1]
        self.add_to_program_block(code=f"(JP, {self.program_block_counter}, , )", line=jump_line)
        self.semantic_stack.pop()

    def label(self, string):
        self.semantic_stack.append(self.program_block_counter)

    def while_end(self, string):
        line_before_while = self.semantic_stack[-3]
        compare_result = self.semantic_stack[-2]
        line_after_while = self.semantic_stack[-1]

        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.pop()

        self.add_to_program_block(code=f"(JP, {line_before_while}, , )")
        self.add_to_program_block(code=f"(JPF, {compare_result}, {self.program_block_counter}, )",
                                  line=line_after_while)

    def assign(self, string):
        a = self.semantic_stack[-1]
        b = self.semantic_stack[-2]
        self.semantic_stack.pop()

        self.add_to_program_block(code=f"(ASSIGN, {a}, {b}, )")

    def find_array_index_address(self, string):
        a = self.semantic_stack[-2]
        i = self.semantic_stack[-1]
        self.semantic_stack.pop()
        self.semantic_stack.pop()

        imul4 = self.symbol_table.get_temp()
        final_address = self.symbol_table.get_temp()

        self.add_to_program_block(code=f"(MULT, {i}, #{self.symbol_table.byte_length}, {imul4})")
        self.add_to_program_block(code=f"(ADD, {a}, #{imul4}, {final_address})")
        self.semantic_stack.append("@" + str(final_address))

    def add_or_sub_or_compare(self, string):
        A = self.semantic_stack[-3]
        op = self.semantic_stack[-2]
        B = self.semantic_stack[-1]

        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.pop()

        result = self.symbol_table.get_temp()

        self.add_to_program_block(code=f"({op}, {A}, {B}, {result})")

        self.semantic_stack.append(result)

    def LT(self, string):
        self.semantic_stack.append('LT')

    def EQ(self, string):
        self.semantic_stack.append('EQ')

    def add_values(self, string):
        self.semantic_stack.append('ADD')

    def sub_values(self, string):
        self.semantic_stack.append('SUB')

    def mult_values(self, string):
        A = self.semantic_stack[-2]
        B = self.semantic_stack[-1]

        self.semantic_stack.pop()
        self.semantic_stack.pop()

        result = self.symbol_table.get_temp()

        self.add_to_program_block(code=f"(MULT, {A}, {B}, {result})")

        self.semantic_stack.append(result)

    def change_sign(self, string):
        A = self.semantic_stack[-1]
        self.semantic_stack.pop()

        result = self.symbol_table.get_temp()

        self.add_to_program_block(code=f"(MULT, {A}, #-1, {result})")

        self.semantic_stack.append(result)

    def print_function(self, string):
        A = self.semantic_stack[-1]
        self.add_to_program_block(code=f"(PRINT, {A}, , )")
        self.semantic_stack.pop()

    def write_output(self, file_name):
        with open(file_name, 'w') as f:
            st_counter = 0
            for s in self.program_block:
                f.write(str(st_counter) + '\t' + s + '\n')
                st_counter += 1
