from SymbolTable import *
from SemanticErrorHandler import SemanticErrorHandler


class FunctionCall:
    def __init__(self, *, mem_size, name):
        self.name = name
        self.mem_size = mem_size


class Subroutines:
    def __init__(self, semantic_checker):
        self.semantic_stack = []
        self.stack = list()
        self.symbol_table = SymbolTable()
        self.program_block = list()
        self.program_block_counter = 0
        self.semantic_checker = semantic_checker
        self.scope_stack = [0]
        self.scope_counter = 1
        self.function_memory = []
        self.function_signature = dict()
        self.code_scope_stack = list()

        self.add_to_program_block(code=f"(ASSIGN, #2000, {self.symbol_table.st_pointer}, )")
        self.add_to_program_block(code=f"(ASSIGN, #0, {self.symbol_table.return_address}, )")

        self.symbol_table.add_symbol(Symbol('output', 'void', 'nothing', 0, 'function', 0, 1))

    def add_to_program_block(self, code, line=None):
        if line is None:
            self.program_block.append(code)
            self.program_block_counter += 1
            # print(self.program_block[-1])
        else:
            self.program_block[line] = code
            # print(self.program_block[line])

    def update_program_block(self, line, str):
        self.program_block[line] = self.program_block[line].replace('?', str)

    def relative_access(self, relative_address):
        tmp = self.symbol_table.get_temp()
        self.add_to_program_block(code=f"(ADD, {self.symbol_table.st_pointer}, #{relative_address}, {tmp})")
        return "@" + str(tmp)

    def reduce_at(self, pointer):
        tmp = self.symbol_table.get_temp()
        self.add_to_program_block(code=f"(ASSIGN, {pointer}, {tmp}, )")
        return '@' + str(tmp)

    def find_symbol_address(self, symbol):
        if symbol is None:
            return None

        if symbol.address_type == 'global':
            return symbol.address

        if symbol.address_type == 'relative':
            return self.relative_access(symbol.address)

        if symbol.address_type == 'relative pointer':
            return self.reduce_at(self.relative_access(symbol.address))

    def close_function(self):
        return_address = self.symbol_table.get_temp()
        self.add_to_program_block(
            code=f"(ADD, {self.symbol_table.st_pointer}, #4, {return_address})")

        self.add_to_program_block(
            code=f"(ASSIGN, @{self.symbol_table.st_pointer}, {self.symbol_table.st_pointer}, )")

        at_at_address = self.symbol_table.get_temp()

        self.add_to_program_block(code=f"(ASSIGN, @{return_address}, {at_at_address}, )")
        self.add_to_program_block(code=f"(JP, @{at_at_address}, ,)")

    def define_function(self, string):
        arguments = []

        while self.semantic_stack[-1] != 'function_start':
            arguments.append(self.semantic_stack.pop())

        arguments.reverse()
        arguments_number = len(arguments) // 3

        self.semantic_stack.pop()

        function_name = self.semantic_stack.pop()
        function_type = self.semantic_stack.pop()

        if function_name != 'main':
            self.add_to_program_block(code="(JP, ?, , )")
            self.semantic_stack.append(self.program_block_counter - 1)

        # print(self.scope_counter)
        # print(len(self.scope_stack))
        self.symbol_table.add_symbol(Symbol(function_name, function_type, "code_line", self.program_block_counter,
                                            'function', self.scope_stack[-1], arguments_number))

        self.scope_counter += 1
        self.scope_stack.append(self.scope_counter)

        self.function_memory.append(FunctionCall(mem_size=8, name=function_name))

        self.function_signature[function_name] = arguments

        i = 0
        while i < len(arguments):
            argument_type = arguments[i]
            argument_name = arguments[i + 1]
            is_array = arguments[i + 2] == 'array'
            # print(is_array)

            type = argument_type
            if is_array:
                type = type + '*'

            print(argument_name, type, is_array)
            self.symbol_table.add_symbol(Symbol(argument_name, type, 'relative', self.function_memory[-1].mem_size,
                                                self.scope_stack[-1], 'variable'))
            # print(self.function_memory[-1].mem_address)
            self.function_memory[-1].mem_size += 4

            i += 3

    def function_start(self, string):
        self.semantic_stack.append("function_start")

    def function_call_start(self, string):
        self.semantic_stack.append("function_call_start")

    def function_return(self, string):
        self.close_function()

    def function_return_with_value(self, string):
        function_result = self.find_symbol_address(self.semantic_stack.pop())
        self.add_to_program_block(code=f"(ASSIGN, {function_result}, {self.symbol_table.return_address}, )")
        self.close_function()

    def end_of_scope(self, string):
        self.symbol_table.delete_scope(self.scope_stack.pop())

    def end_of_function(self, string):
        function_values = self.function_memory.pop()
        if function_values.name != 'main':
            self.close_function()
            function_jump_line_in_program_block = self.semantic_stack.pop()
            self.update_program_block(function_jump_line_in_program_block, str(self.program_block_counter))

    def function_call(self, string):
        arguments = []
        while self.semantic_stack[-1] != 'function_call_start':
            arguments.append(self.semantic_stack.pop())

        arguments.reverse()

        self.semantic_stack.pop()
        function_symbol = self.semantic_stack.pop()

        if function_symbol is None:
            self.semantic_stack.append(None)
            return
        if len(arguments) != function_symbol.arguments_count:
            self.semantic_checker.arguments_count_error(function_symbol.name)
            self.semantic_stack.append(None)
            return

        if function_symbol.name == 'output':
            self.add_to_program_block(code=f"(PRINT, {self.find_symbol_address(arguments[0])}, , )")
            self.semantic_stack.append('output function void')
            return

        stack_pointer_new_address = self.symbol_table.get_temp()
        print(f"(ADD, {self.symbol_table.st_pointer}, #{self.function_memory[-1].mem_size}, {stack_pointer_new_address})")

        self.add_to_program_block(
            code=f"(ADD, {self.symbol_table.st_pointer}, #{self.function_memory[-1].mem_size}, {stack_pointer_new_address})")
        self.add_to_program_block(
            code=f"(ASSIGN, {self.symbol_table.st_pointer}, @{stack_pointer_new_address}, )")

        return_address = self.symbol_table.get_temp()
        self.add_to_program_block(
            code=f"(ADD, {self.symbol_table.st_pointer}, #{self.function_memory[-1].mem_size + 4}, {return_address})")

        i = 0
        while i < len(arguments):
            argument = arguments[i]

            if self.function_signature[function_symbol.name][3 * i + 2] != 'array' and argument.variable_type == 'int*':
                self.semantic_checker.argument_type_error(
                    self.function_signature[function_symbol.name][3 * i], function_symbol.name, 'int', 'array')

            if self.function_signature[function_symbol.name][3 * i + 2] == 'array' and argument.variable_type == 'int':
                self.semantic_checker.argument_type_error(
                    self.function_signature[function_symbol.name][3 * i], function_symbol.name, 'array', 'int')

            argument_address = self.symbol_table.get_temp()

            self.add_to_program_block(
                code=f"(ADD, {self.symbol_table.st_pointer}, #{self.function_memory[-1].mem_size + 8 + i  * 4},"
                     f" {argument_address})")

            self.add_to_program_block(code=f"(ASSIGN, {self.find_symbol_address(argument)}, @{argument_address}, )")

            i += 1

        self.add_to_program_block(
            code=f"(ASSIGN, {stack_pointer_new_address}, {self.symbol_table.st_pointer}, )")

        self.add_to_program_block(code=f"(ASSIGN, #{self.program_block_counter + 2}, @{return_address}, )")

        self.add_to_program_block(code=f"(JP, {function_symbol.address}, ,)")

        relative_address = self.function_memory[-1].mem_size
        function_result_address = self.relative_access(relative_address)
        self.function_memory[-1].mem_size += 4

        self.add_to_program_block(
            code=f"(ASSIGN, {self.symbol_table.return_address}, {function_result_address}, )")

        self.semantic_stack.append(
            Symbol("", function_symbol.variable_type, 'relative', relative_address, -1, 'variable'))

    def push_number(self, string):
        temp = self.symbol_table.get_temp()
        value = int(string)
        self.add_to_program_block(code=f"(ASSIGN, #{value}, {temp}, )")
        symbol = Symbol(name="", variable_type='int', address_type='global', address=temp, scope=-1,
                        symbol_type='variable')
        self.semantic_stack.append(symbol)

    def pop_number(self, string):
        self.semantic_stack.pop()

    def push_id(self, string):
        try:
            symbol = self.symbol_table.find_address(string)
            self.semantic_stack.append(symbol)
        except:
            self.semantic_checker.undefined_error(string)
            self.semantic_stack.append(None)

    def push(self, string):
        self.semantic_stack.append(string)

    def push_array_type(self, string):
        self.semantic_stack.append('array')

    def push_non_type(self, string):
        self.semantic_stack.append('nothing')

    def define_variable(self, string):
        variable_type = self.semantic_stack[-2]
        variable_name = self.semantic_stack[-1]
        self.semantic_stack = self.semantic_stack[:-2]

        if variable_type == 'void':
            self.semantic_checker.void_error(variable_name)
            return

        if self.function_memory:
            symbol = Symbol(name=variable_name, variable_type=variable_type, address_type="relative",
                            address=self.function_memory[-1].mem_size, scope=self.scope_stack[-1],
                            symbol_type='variable')
            self.function_memory[-1].mem_size += 4
            self.symbol_table.symbols.append(symbol)
        else:
            symbol = Symbol(name=variable_name, variable_type=variable_type, address_type="global",
                            address=self.symbol_table.get_global(), scope=self.scope_stack[-1],
                            symbol_type='variable')
            self.symbol_table.symbols.append(symbol)

    def define_array(self, string):
        array_type = self.semantic_stack[-3]
        array_name = self.semantic_stack[-2]
        array_len = self.semantic_stack[-1]
        self.semantic_stack = self.semantic_stack[:-3]

        if array_type == 'void':
            self.semantic_checker.void_error(array_name)
            return

        if self.function_memory:
            symbol = Symbol(name=array_name, variable_type=f'{array_name}*', address_type='relative',
                            address=self.function_memory[-1].mem_size, scope=self.scope_stack[-1],
                            symbol_type='variable')

            ptr_address = self.relative_access(self.function_memory[-1].mem_size)
            self.function_memory[-1].mem_size += 4
            address = self.relative_access(self.function_memory[-1].mem_size)
            self.add_to_program_block(code=f'(ASSIGN, {address[1:]}, {ptr_address}, )')
            self.function_memory[-1].mem_size += 4 * int(array_len)

            self.symbol_table.symbols.append(symbol)
        else:
            ptr_address = self.symbol_table.get_temp()
            allocation_address = self.symbol_table.make_space(array_len)
            self.add_to_program_block(code=f'(ASSIGN, #{allocation_address}, {ptr_address}, )')

            symbol = Symbol(name=array_name, variable_type=(array_type + '*'), address_type='global',
                            address=ptr_address, scope=self.scope_stack[-1], symbol_type='variable')
            self.symbol_table.symbols.append(symbol)

    def array_space(self, string):
        self.symbol_table.make_space(int(string))

    def save_address(self, string):
        self.semantic_stack.append(self.program_block_counter)
        self.add_to_program_block(code=None)

    def start_if(self, string):
        print('%', self.semantic_stack[-1])
        result_address = self.find_symbol_address(self.semantic_stack[-1])
        self.semantic_stack.pop()
        self.add_to_program_block(f'(JPF, {result_address}, ?, )')
        self.semantic_stack.append(self.program_block_counter - 1)

    def start_else(self, string):
        self.add_to_program_block(f'(JP, ?, , )')
        if_line = self.semantic_stack[-1]
        self.semantic_stack.pop()
        self.semantic_stack.append(self.program_block_counter - 1)
        self.program_block[if_line] = self.program_block[if_line].replace('?', str(self.program_block_counter))

    def end_if(self, string):
        else_line = self.semantic_stack[-1]
        self.semantic_stack.pop()
        self.program_block[else_line] = self.program_block[else_line].replace('?', str(self.program_block_counter))

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
        a = self.find_symbol_address(self.semantic_stack[-1])
        b = self.find_symbol_address(self.semantic_stack[-2])
        self.semantic_stack.pop()

        self.add_to_program_block(code=f"(ASSIGN, {a}, {b}, )")

    def find_array_index_address(self, string):
        a = self.semantic_stack[-2]
        i = self.semantic_stack[-1]
        self.semantic_stack.pop()
        self.semantic_stack.pop()

        a = self.find_symbol_address(a)
        i = self.find_symbol_address(i)

        final_address = self.function_memory[-1].mem_size
        temp_address = self.relative_access(final_address)

        symbol = Symbol(name="", variable_type='int', address_type='relative pointer',
                        address=self.function_memory[-1].mem_size, scope=-1, symbol_type='variable')
        self.semantic_stack.append(symbol)

        self.function_memory[-1].mem_size += 4
        self.add_to_program_block(code=f"(ADD, {a}, {i}, {temp_address})")

    def is_int(self, *args):
        flag = False
        for symbol in args:
            if symbol is None:
                continue
            if symbol.variable_type == 'int*':
                self.semantic_checker.type_operation_error('array', 'int')
                flag = True
            if symbol.variable_type == 'function':
                self.semantic_checker.type_operation_error('function', 'int')
                flag = True
        return flag

    def add_or_sub_or_compare(self, string):
        A = self.semantic_stack[-3]
        op = self.semantic_stack[-2]
        B = self.semantic_stack[-1]

        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.pop()

        self.is_int(A, B)

        A = self.find_symbol_address(A)
        B = self.find_symbol_address(B)

        relative_address = self.function_memory[-1].mem_size
        result = self.relative_access(self.function_memory[-1].mem_size)
        self.function_memory[-1].mem_size += 4

        self.add_to_program_block(code=f"({op}, {A}, {B}, {result})")

        symbol = Symbol(name="", variable_type='int', address_type='relative', address=relative_address, scope=-1,
                        symbol_type='variable')
        self.semantic_stack.append(symbol)

    def LT(self, string):
        self.semantic_stack.append('LT')

    def EQ(self, string):
        self.semantic_stack.append('EQ')

    def add_values(self, string):
        self.semantic_stack.append('ADD')

    def sub_values(self, string):
        self.semantic_stack.append('SUB')

    def mult_values(self, string):
        A = self.find_symbol_address(self.semantic_stack[-2])
        B = self.find_symbol_address(self.semantic_stack[-1])

        self.semantic_stack.pop()
        self.semantic_stack.pop()

        relative_address = self.function_memory[-1].mem_size
        result = self.relative_access(relative_address)
        self.function_memory[-1].mem_size += 4

        self.add_to_program_block(code=f"(MULT, {A}, {B}, {result})")

        symbol = Symbol(name="", variable_type='int', address_type='relative', address=relative_address, scope=-1,
                        symbol_type='variable')
        self.semantic_stack.append(symbol)

    def start_while(self, string):
        self.code_scope_stack.append(('while', len(self.semantic_stack)))
        self.add_to_program_block(code=f"(JP, {self.program_block_counter + 2}, , )")
        self.semantic_stack.append(self.program_block_counter)
        self.add_to_program_block(code="(JP, ?, , )")
        self.semantic_stack.append(self.program_block_counter)

    def while_condition(self, string):
        result = self.find_symbol_address(self.semantic_stack[-1])
        self.semantic_stack.pop()
        self.add_to_program_block(code=f'(JPF, {result}, ?, )')
        self.semantic_stack.append(self.program_block_counter - 1)

    def end_while(self, string):
        condition_line = self.semantic_stack[-1]
        beginning_line = self.semantic_stack[-2]
        outer_line = self.semantic_stack[-3]

        self.semantic_stack = self.semantic_stack[:-3]
        self.add_to_program_block(code=f'(JP, {beginning_line}, , )')
        self.program_block[condition_line] = self.program_block[condition_line].replace('?',
                                                                                        str(self.program_block_counter))
        self.program_block[outer_line] = self.program_block[outer_line].replace('?', str(self.program_block_counter))

        self.code_scope_stack.pop()

    def start_switch(self, string):
        self.code_scope_stack.append(("switch", len(self.semantic_stack)))
        self.add_to_program_block(code=f'(JP, {self.program_block_counter + 2}, , )')
        self.semantic_stack.append(self.program_block_counter)
        self.add_to_program_block(code=f'(JP, ?, , )')

    def end_switch(self, string):
        outer_line = self.semantic_stack[-2]
        self.program_block[outer_line] = self.program_block[outer_line].replace('?', str(self.program_block_counter))

        self.semantic_stack = self.semantic_stack[:-2]
        self.code_scope_stack.pop()

    def start_case(self, string):
        case_address = self.find_symbol_address(self.semantic_stack[-1])
        switch_address = self.find_symbol_address(self.semantic_stack[-2])
        self.semantic_stack.pop()

        result_address = self.symbol_table.get_temp()
        self.add_to_program_block(code=f'(EQ, {case_address}, {switch_address}, {result_address})')
        self.semantic_stack.append(self.program_block_counter)
        self.add_to_program_block(code=f'(JPF, {result_address}, ?, )')

    def end_case(self, string):
        condition_line = self.semantic_stack[-1]
        self.program_block[condition_line] = self.program_block[condition_line].replace('?',
                                                                                        str(self.program_block_counter))
        self.semantic_stack.pop()

    def break_command(self, string):
        if self.code_scope_stack:
            jump_line = self.semantic_stack[self.code_scope_stack[-1][1]]
            self.add_to_program_block(code=f'(JP, {jump_line}, , )')
        else:
            self.semantic_checker.break_error()

    def change_sign(self, string):
        A = self.semantic_stack[-1]
        self.semantic_stack.pop()

        self.is_int(A)

        A = self.find_symbol_address(A)
        relative_address = self.function_memory[-1].mem_size
        result = self.relative_access(relative_address)
        self.function_memory[-1].mem_size += 4

        self.add_to_program_block(code=f"(MULT, {A}, #-1, {result})")

        symbol = Symbol(name="", variable_type='int', address_type='relative', address=relative_address, scope=-1,
                        symbol_type='variable')
        self.semantic_stack.append(symbol)

    def print_function(self, string):
        A = self.semantic_stack[-1]
        self.add_to_program_block(code=f"(PRINT, {A}, , )")
        self.semantic_stack.pop()

    def write_output(self, file_name):
        with open(file_name, 'w') as f:
            if self.semantic_checker.errors:
                f.write('The code has not been generated.\n')
                return
            st_counter = 0
            for s in self.program_block:
                # print(s)
                f.write(str(st_counter) + '\t' + s + '\n')
                st_counter += 1
