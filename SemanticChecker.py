class SemanticChecker:
    def __init__(self, parser):
        self.parser = parser.scanner
        self.errors = list()

    def break_error(self):
        self.errors.append(f'#{self.parser.scanner.tk_counter} : Semantic Error! ' +
                           "No 'while' or 'switch' found for 'break'.")

    def undefined_error(self, variable_name):
        self.errors.append(f'#{self.parser.scanner.tk_counter} : Semantic Error! ' +
                           f"{variable_name} is not defined.")

    def void_error(self, variable_name):
        self.errors.append(f'#{self.parser.scanner.tk_counter} : Semantic Error! ' +
                           f"Illegal type of void for {variable_name}'.")

    def arguments_count_error(self, function_name):
        self.errors.append(f'#{self.parser.scanner.tk_counter} : Semantic Error! ' +
                           f"Mismatch in numbers of arguments of {function_name}.")

    def type_operation_error(self, type1, type2):
        self.errors.append(f'#{self.parser.scanner.tk_counter} : Semantic Error! ' +
                           f"Type mismatch in operands, Got {type1} instead of {type2}.\n")

    def argument_type_error(self, variable_name, function_name, type1, type2):
        self.errors.append(f'#{self.parser.scanner.tk_counter} : Semantic Error! ' +
                           f"Mismatch in type of argument {variable_name} of {function_name}'." +
                           f"Expected {type1} but got {type2} instead.")

    def write_output(self, file_name):
        with open(file_name, 'w') as f:
            for line in self.errors:
                f.write(line + '\n')
