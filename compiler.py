# Ali Shafiee 			97110122
# Shayan Cheshm Jahan	97110047

from scanner import Scanner

if __name__ == '__main__':
    scanner = Scanner('input.txt')
    scanner.init_states()

    while scanner.get_next_token()[0] != '$':
        pass

    scanner.write_tokens('tokens.txt')

    if scanner.current_state == 11 or scanner.current_state == 13:
        scanner.lexical_errors[scanner.last_comment_line].append(
            "(" + scanner.current_string[:7] + "..., " + "Unclosed comment) ")

    scanner.write_lexical_errors('lexical_errors.txt')
    scanner.write_symbol_table('symbol_table.txt')
    scanner.close()
