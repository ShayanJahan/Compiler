class Scanner:
    def __init__(self, input_name):
        self.mat = [dict() for _ in range(16)]
        self.oth = [0] * 16
        self.mark = [False] * 16
        self.term = [False] * 16
        self.have_star = [False] * 16
        self.message = [''] * 16
        self.symbols_list = ["if", "else", "void", "int", "while", "break", "switch", "default", "case", "return"]
        self.valid_chars = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '/', ' ', '\n', '\t']
        self.keywords = ["if", "else", "void", "int", "while", "break", "switch", "default", "case", "return",
                         "continue"]

        self.current_state = 0
        self.current_string = ""
        self.tk_counter = 1
        self.in_comment_all = False
        self.last_comment_line = -1
        self.lexical_errors = [list() for _ in range(10000)]
        self.in_comment_line = False
        self.tokens = [list() for _ in range(10000)]
        self.all_tokens = list()

        self.input_file = open(input_name, 'r')

    def close(self):
        self.input_file.close()

    def init_states(self):
        self.mat[0]["letter"] = 1
        self.mat[0]["digit"] = 3
        self.mat[0][";"] = 5
        self.mat[0][":"] = 5
        self.mat[0][","] = 5
        self.mat[0]["["] = 5
        self.mat[0]["]"] = 5
        self.mat[0]["("] = 5
        self.mat[0][")"] = 5
        self.mat[0]["{"] = 5
        self.mat[0]["}"] = 5
        self.mat[0]["+"] = 5
        self.mat[0]["-"] = 5
        self.mat[0]["<"] = 5
        self.mat[0]["="] = 6
        self.mat[0]["*"] = 8
        self.mat[0]["/"] = 10
        self.mat[0][" "] = 15
        self.mat[0]["\n"] = 15
        self.mat[0]["\t"] = 15
        self.mat[0]["\r"] = 15
        self.mat[0]["\f"] = 15
        self.mat[0]["\v"] = 15
        self.oth[0] = -1
        self.message[0] = "Invalid input"

        self.mat[1]["letter"] = 1
        self.mat[1]["digit"] = 1
        self.oth[1] = 2

        self.term[2] = True
        self.mark[2] = True
        self.have_star[2] = True

        self.mat[3]["digit"] = 3
        self.mat[3]["letter"] = -1
        self.oth[3] = 4
        self.message[3] = "Invalid number"

        self.term[4] = True
        self.mark[4] = True
        self.have_star[4] = True

        self.term[5] = True

        self.mat[6]["="] = 7
        self.oth[6] = 9

        self.term[7] = True

        self.mat[8]["/"] = -1
        self.oth[8] = 9
        self.message[8] = "Unmatched comment"

        self.term[9] = True
        self.mark[9] = True
        self.have_star[9] = True

        self.mat[10]["/"] = 11
        self.mat[10]["*"] = 13
        self.oth[10] = -1
        self.message[10] = "Invalid input"

        self.mat[11]["\n"] = 12
        self.oth[11] = 11

        self.term[12] = True

        self.mat[13]["*"] = 14
        self.oth[13] = 13

        self.mat[14]["/"] = 12
        self.mat[14]["*"] = 14
        self.oth[14] = 13

        self.term[15] = True

    def find_type(self, char):
        if ('a' <= char <= 'z') or ('A' <= char <= 'Z'):
            return "letter"

        if '0' <= char <= '9':
            return "digit"

        if char in self.valid_chars:
            return char

        return '!'

    def is_in_keyword(self, string):
        return string in self.keywords

    def process_next_char(self, c):
        if c == '\n':
            if not self.in_comment_all:
                self.current_state = 0

            self.tk_counter = self.tk_counter + 1
            self.in_comment_line = False

        fin = False

        while not fin:
            fin = True

            in_comment = False
            if self.current_state == 11 or self.current_state == 13:
                in_comment = True

            self.current_string = self.current_string + c

            t = self.find_type(c)
            if not self.in_comment_all and not self.in_comment_line and t == '!':
                if self.current_string[0:-1] == "/":
                    if len(self.current_string[0:-1]) > 0:
                        self.lexical_errors[self.tk_counter].append(
                            "(" + self.current_string[0:-1] + ", " + "Invalid input" + ") ")
                    self.lexical_errors[self.tk_counter].append("(" + c + ", " + "Invalid input" + ") ")
                    self.current_state = 0
                    self.current_string = ""
                else:
                    self.lexical_errors[self.tk_counter].append(
                        "(" + self.current_string + ", " + "Invalid input" + ") ")
                    self.current_state = 0
                    self.current_string = ""
            elif t in self.mat[self.current_state]:
                if self.mat[self.current_state][t] == -1:
                    if c == ' ' or c == '\n' or c == '\t':
                        self.current_string = self.current_string[0: -1]
                    self.lexical_errors[self.tk_counter].append(
                        "(" + self.current_string + ", " + self.message[self.current_state] + ") ")

                self.current_state = self.mat[self.current_state][t]
            # print("-> " + str(current_state))
            else:
                if self.oth[self.current_state] == -1 and self.current_state == 10:
                    fin = False
                    self.current_string = self.current_string[0: -1]
                    self.lexical_errors[self.tk_counter].append(
                        "(" + self.current_string + ", " + self.message[self.current_state] + ") ")
                elif self.oth[self.current_state] == -1:
                    if c == ' ' or c == '\n' or c == '\t':
                        self.current_string = self.current_string[0: -1]
                    self.lexical_errors[self.tk_counter].append(
                        "(" + self.current_string + ", " + self.message[self.current_state] + ") ")

                self.current_state = self.oth[self.current_state]
                # print("-> " + str(current_state))
                if self.current_state == -1:
                    self.current_state = 0
                    self.current_string = ""

            if self.current_state == 11:
                self.in_comment_line = True
                if not in_comment:
                    self.last_comment_line = self.tk_counter

            if self.current_state == 13:
                self.in_comment_all = True
                if not in_comment:
                    self.last_comment_line = self.tk_counter

            if self.term[self.current_state]:
                if self.have_star[self.current_state]:
                    fin = False
                    self.current_string = self.current_string[0: -1]

                if self.current_state == 2:
                    flag = False
                    for s in self.symbols_list:
                        if s == self.current_string:
                            flag = True

                    if not self.is_in_keyword(self.current_string) and not flag:
                        self.symbols_list.append(self.current_string)

                    if self.is_in_keyword(self.current_string):
                        self.add_token("KEYWORD", self.current_string)
                    else:
                        self.add_token("ID", self.current_string)

                elif self.current_state == 4:
                    self.add_token("NUM", self.current_string)
                elif self.current_state == 5 or self.current_state == 7 or self.current_state == 9:
                    self.add_token("SYMBOL", self.current_string)

                elif self.current_state == 12:
                    self.in_comment_all = False
                    self.in_comment_line = False

                self.current_state = 0
                self.current_string = ""

    def get_next_token(self):
        while True:
            char = self.input_file.read(1)
            if char == '$' or char == '':
                return '$', 'END OF FILE'
            prev_len = len(self.all_tokens)
            self.process_next_char(char)
            if len(self.all_tokens) > prev_len:
                return self.all_tokens[-1]

    def add_token(self, token_type, string):
        self.all_tokens.append((token_type, string))
        self.tokens[self.tk_counter].append((token_type, string))

    def write_tokens(self, file_name):
        with open(file_name, 'w') as f:
            for line_id in range(10000):
                if not self.tokens[line_id]:
                    continue
                f.write(str(line_id) + '.\t')
                f.write(' '.join(f'({token_type}, {string})' for token_type, string in self.tokens[line_id]))
                f.write('\n')

    def write_lexical_errors(self, file_name):
        with open(file_name, 'w') as LE:
            flag = False
            for i in range(10000):
                if len(self.lexical_errors[i]) == 0:
                    continue

                flag = True
                LE.write(str(i) + ".\t")
                LE.write(' '.join(s[0: -1] for s in self.lexical_errors[i]))
                LE.write('\n')

            if not flag:
                LE.write("There is no lexical error.")

    def write_symbol_table(self, file_name):
        with open(file_name, 'w') as ST:
            st_counter = 0
            for s in self.symbols_list:
                st_counter += 1
                ST.write(str(st_counter) + ".\t" + s + '\n')
