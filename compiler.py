# Ali Shafiee 			97110122
# Shayan Cheshm Jahan	97110047

from scanner import Scanner

if __name__ == '__main__':
    scanner = Scanner('input.txt')
    scanner.init_states()

    while scanner.get_next_token()[0] != '$':
        pass

    scanner.write_tokens('tokens.txt')
    scanner.write_lexical_errors('lexical_errors.txt')
    scanner.write_symbol_table('symbol_table.txt')

    scanner.close()
