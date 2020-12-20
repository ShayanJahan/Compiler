from SymbolTable import SymbolTable

class Subroutines:
    def __init__(self):
        self.semantic_stack = []
        program_block = []
        program_block_counter = 0

        symbol_table = SymbolTable()

        self.stack = list()
        self.symbol_table = SymbolTable()
        self.program_block = list()
        program_block = 0

    def self.add_to_program_block(self, str: string):
        self.program_block.append(str)

    def push_number(self, str: string):
        temp = symbol_table.get_temp();
        value = int(str)
        self.add_to_program_block(code = "(ASSIGN, #%s, %d, )" % (value, temp))
        self.semantic_stack.append(temp)

    def pop_number (self, str: string):
        self.semantic_stack.pop()

    def push_id (self, str: string):
        self.semantic_stack.append(symbol_table.find_address(str))

    def define_variable (self, str: string):
        symbol_table.find_address(str)

    def array_space (self, str: string):
        symbol_table.extend(int(str))

    def save_adress (self, str: string):
        self.semantic_stack.append(program_block_counter)
        self.add_to_program_block(code = None)

    def false_condition_jump (self, str: string):
        compare_result = self.semantic_stack[-2]
        jump_line = self.semantic_stack[-1]

        self.semantic_stack.pop()
        self.semantic_stack.pop()

        self.semantic_stack.append(program_block_counter)

        self.add_to_program_block(code = None)
        self.add_to_program_block(code = "(JPF, %s, %s, )" % (compare_result, program_block_counter), line_number = jump_line)

    def jump (self, str: string):
        jump_line = self.semantic_stack[-1]
        self.add_to_program_block(code = "(JP, %s, , )" % program_block_counter, line_number = jump_line)
        self.semantic_stack.pop()

    def label (self, str: string):
        self.semantic_stack.append(program_block_counter)

    def while_end (self, str: string):
        line_before_while = self.semantic_stack[-3]
        compare_result = self.semantic_stack[-2]
        line_after_while = self.semantic_stack[-1]

        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.pop()

        self.add_to_program_block(code = "(JP, %s, , )" % line_before_while)
        self.add_to_program_block(code = "(JPF, %s, %s, )" % (compare_result, program_block_counter),
                    line_number = line_after_while)

    def assign (self, str: string):
        A = self.semantic_stack[-1]
        R = self.semantic_stack[-2]
        self.semantic_stack.pop()

        self.add_to_program_block(code="(ASSIGN, %s, %s, )" % (A, R))

    def find_array_index_address (self, str: string):
        a = self.semantic_stack[-2]
        i = self.semantic_stack[-1]
        self.semantic_stack.pop()
        self.semantic_stack.pop()

        imul4 = symbol_table.get_temp()
        final_address = symbol_table.get_temp()

        self.add_to_program_block(code="(MULT, %s, #4, %s)" % (i, imul4))
        self.add_to_program_block(code="(ADD, %s, #%s, %s)" % (a, imul4, final_address))
        self.semantic_stack.append("@" + str(final_address))

    def compare (self, str: string):
        A = self.semantic_stack[-3]
        op = self.semantic_stack[-2]
        B = self.semantic_stack[-1]

        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.pop()

        result = symbol_table.get_temp()

        self.add_to_program_block(code = "(%s, %s, %s, %s)" % (op, A, B, result))

        self.semantic_stack.append(result)

    def LT (self, str: string):
        self.semantic_stack.append('LT')

    def EQ (self, str: string):
        self.semantic_stack.append('EQ')

    def add_or_sub (self, str: string):
        A = self.semantic_stack[-3]
        op = self.semantic_stack[-2]
        B = self.semantic_stack[-1]

        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.pop()

        result = symbol_table.get_temp()

        self.add_to_program_block(code = "(%s, %s, %s, %s)" % (op, A, B, result))

        self.semantic_stack.append(result)

    def add_values (self, str: string):
        self.semantic_stack.append('ADD')

    def sub_values (self, str: string):
        self.semantic_stack.append('SUB')

    def mult_values (self, str: string):
        A = self.semantic_stack[-2]
        B = self.semantic_stack[-1]

        self.semantic_stack.pop()
        self.semantic_stack.pop()

        result = symbol_table.get_temp()

        self.add_to_program_block(code="(MULT, %s, %s, %s)" % (A, B, result))

        self.semantic_stack.append(result)

    def change_sign (self, str: string):
        A = self.semantic_stack[-1]
        self.semantic_stack.pop()

        result = symbol_table.get_temp()

        self.add_to_program_block(code="(MULT, %s, #-1, %s)" % (A, result))

        self.semantic_stack.append(result)
