# Ali Shafiee 			97110122
# Shayan Cheshm Jahan	97110047

from scanner import Scanner
from parser import Parser

if __name__ == '__main__':
    scanner = Scanner('input.txt')
    scanner.init_states()

    parser = Parser(scanner)
    parser.start()

    parser.write_tree('pars_tree.txt')
    parser.write_syntax_errors('syntax_errors.txt')

    scanner.write_tokens('tokens.txt')
    scanner.write_lexical_errors('lexical_errors.txt')
    scanner.write_symbol_table('symbol_table.txt')

    parser.subroutines.write_output('output.txt')

    scanner.close()
