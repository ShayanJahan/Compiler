import anytree
from CodeGenerator import Subroutines
from SemanticErrorHandler import SemanticErrorHandler

EPSILON = 'ε'


class Parser:

    def __init__(self, scanner):
        self.non_terminals = set()
        self.grammar = list()
        self.open_grammar()
        self.first_set = dict()
        self.open_firsts()
        self.follow_set = dict()
        self.open_follows()
        self.table = dict([(state, dict()) for state in self.non_terminals])
        self.open_predicts()
        self.add_sync()
        self.scanner = scanner
        self.errors = list()
        self.root = None
        self.semantic_checker = SemanticErrorHandler(self)
        self.subroutines = Subroutines(self.semantic_checker)

    def open_grammar(self):
        with open('grammar.txt', 'r') as grammar_file:
            for line in grammar_file.readlines():
                ls = line.split()
                self.grammar.append((ls[0], ls[2:]))
                self.non_terminals.add(ls[0])

    def open_firsts(self):
        with open('firsts.txt', 'r') as first_file:
            for line in first_file.readlines():
                ls = line.split()
                self.first_set[ls[0]] = set(ls[1:])

    def open_follows(self):
        with open('follows.txt', 'r') as follow_file:
            for line in follow_file.readlines():
                ls = line.split()
                self.follow_set[ls[0]] = set(ls[1:])

    def open_predicts(self):
        with open('predicts.txt', 'r') as predict_file:
            for line, (state, rule) in zip(predict_file.readlines(), self.grammar):
                ls = line.split()
                for terminal in ls:
                    self.table[state][terminal] = rule

    def add_sync(self):
        for non_terminal in self.non_terminals:
            if EPSILON not in self.first_set[non_terminal]:
                for follow in self.follow_set[non_terminal]:
                    if follow not in self.first_set[non_terminal]:
                        self.table[non_terminal][follow] = 'sync'

    def add_error(self, message):
        self.errors.append((self.scanner.tk_counter, message))

    def start(self):
        token_type, token_string = self.scanner.get_next_token()
        prev_string = None
        stack = [('Program', None)]

        while stack:
            state, parent = stack.pop()
            current_node = anytree.Node(state)

            if parent:
                current_node.parent = parent
            else:
                self.root = current_node

            if state == EPSILON:
                current_node.name = 'epsilon'
                continue

            if state.startswith('#'):
                func_name = state[1:]
                getattr(self.subroutines, func_name)(string=prev_string)
                continue

            if state in self.non_terminals:
                while token_type not in self.table[state] and token_type != '$':
                    self.add_error(f'syntax error, illegal {token_type}')
                    prev_string = token_type
                    token_type, token_string = self.scanner.get_next_token()

                if token_type == '$' and token_type not in self.table[state]:
                    self.add_error('syntax error, unexpected EOF')
                    current_node.parent = None
                    break
                elif self.table[state][token_type] == 'sync':
                    self.add_error(f'syntax error, missing {state}')
                    current_node.parent = None
                else:
                    for char in reversed(self.table[state][token_type]):
                        stack.append((char, current_node))
            else:
                if state == token_type or state == token_string:
                    if token_type in {'ID', 'NUM'}:
                        token_type, token_string = token_string, token_type
                    current_node.name = f'({token_string}, {token_type})'
                    prev_string = token_type
                    token_type, token_string = self.scanner.get_next_token()
                else:
                    self.add_error(f'syntax error, missing {state}')
                    current_node.parent = None

    def write_tree(self, file_name):
        with open(file_name, 'w') as tree_file:
            tree_file.write(anytree.RenderTree(self.root).by_attr(attrname="name"))

    def write_syntax_errors(self, file_name):
        with open(file_name, 'w') as syntax_file:
            if self.errors:
                syntax_file.write('\n'.join(f'#{a} : {b}' for a, b in self.errors))
            else:
                syntax_file.write('There is no syntax error.')
