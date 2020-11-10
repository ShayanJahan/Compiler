# Ali Shafiee 			97110122
# Shayan Cheshm Jahan	97110047

from typing import Dict

# Initializing states
mat = [dict() for i in range(16)]
oth = [int() for i in range(16)]
mark = [bool() for i in range(16)]
term = [bool() for i in range(16)]
have_star = [bool() for i in range(16)]
message = [str() for i in range(16)]

def init_states():
	mat[0]["letter"] = 1
	mat[0]["digit"] = 3
	mat[0][";"] = 5
	mat[0][":"] = 5
	mat[0][","] = 5
	mat[0]["["] = 5
	mat[0]["]"] = 5
	mat[0]["("] = 5
	mat[0][")"] = 5
	mat[0]["{"] = 5
	mat[0]["}"] = 5
	mat[0]["+"] = 5
	mat[0]["-"] = 5
	mat[0]["<"] = 5
	mat[0]["="] = 6
	mat[0]["*"] = 8
	mat[0]["/"] = 10
	mat[0][" "] = 15
	mat[0]["\n"] = 15
	mat[0]["\t"] = 15
	mat[0]["\r"] = 15
	mat[0]["\f"] = 15
	mat[0]["\v"] = 15
	oth[0] = -1
	message[0] = "Invalid input"

	mat[1]["letter"] = 1
	mat[1]["digit"] = 1
	oth[1] = 2

	term[2] = True
	mark[2] = True
	have_star[2] = True

	mat[3]["digit"] = 3
	mat[3]["letter"] = -1
	oth[3] = 4
	message[3] = "Invalid number"

	term[4] = True
	mark[4] = True
	have_star[4] = True

	term[5] = True

	mat[6]["="] = 7
	oth[6] = 9

	term[7] = True

	mat[8]["/"] = -1
	oth[8] = 9
	message[8] = "Unmatched comment"

	term[9] = True
	mark[9] = True
	have_star[9] = True

	mat[10]["/"] = 11
	mat[10]["*"] = 13
	oth[10] = -1
	message[10] = "Invalid input"

	mat[11]["\n"] = 12
	oth[11] = 11

	term[12] = True

	mat[13]["*"] = 14
	oth[13] = 13

	mat[14]["/"] = 12
	mat[14]["*"] = 14
	oth[14] = 13

	term[15] = True


# INP is for input.txt
INP = open("input.txt", "r")
# ST is for symbol_table.txt
ST = open("symbol_table.txt", "w")
# LE is for lexical_error.txt
LE = open("lexical_errors.txt", "w")
# TK is for tokens.txt
TK = open("tokens.txt", "w")

symbols_list = ["if", "else", "void", "int", "while", "break", "switch", "default", "case", "return"]

st_counter = 0

init_states()

valid_chars = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '/', ' ', '\n', '\t']


def find_type(char):
	if ('a' <= char <= 'z') or ('A' <= char <= 'Z'):
		return "letter"

	if '0' <= char <= '9':
		return "digit"

	for c in valid_chars:
		if char == c:
			return char

	return '!'


keywords = ["if", "else", "void", "int", "while", "break", "switch", "default", "case", "return", "continue"]


def is_in_keyword(str):
	for key in keywords:
		if str == key:
			return True

	return False


current_state = 0
current_string = ""

tk_counter = 0

in_comment_all = False
current_state = 0

last_comment_line = -1

lexical_errors = [list() for i in range(10000)]

TFL = False

for s in INP.readlines():
	if not in_comment_all:
		current_state = 0
	tk_counter = tk_counter + 1

	line_number_printed = False
	tk_sh = False

	in_comment_line = False

	for c in s:
		fin = False

		while not fin:
			fin = True

			in_comment = False
			if current_state == 11 or current_state == 13:
				in_comment = True

			#print(str(current_state) + " + " + find_type(c))
			current_string = current_string + c

			t = find_type(c)
			if not in_comment_all and not in_comment_line and t == '!':
				if current_string[0:-1] == "/":
					if len(current_string[0:-1]) > 0:
						lexical_errors[tk_counter].append("(" + current_string[0:-1] + ", " + "Invalid input" + ") ")
					lexical_errors[tk_counter].append("(" + c + ", " + "Invalid input" + ") ")
					current_state = 0
					current_string = ""
				else:
					lexical_errors[tk_counter].append("(" + current_string + ", " + "Invalid input" + ") ")
					current_state = 0
					current_string = ""
			elif t in mat[current_state]:
				if mat[current_state][t] == -1:
					if c == ' ' or c == '\n' or c == '\t':
						current_string = current_string[0: -1]
					lexical_errors[tk_counter].append("(" + current_string + ", " + message[current_state] + ") ")

				current_state = mat[current_state][t]
				#print("-> " + str(current_state))
			else:
				if oth[current_state] == -1 and current_state == 10:
					fin = False
					current_string = current_string[0: -1]
					lexical_errors[tk_counter].append("(" + current_string + ", " + message[current_state] + ") ")
				elif oth[current_state] == -1:
					if c == ' ' or c == '\n' or c == '\t':
						current_string = current_string[0: -1]
					lexical_errors[tk_counter].append("(" + current_string + ", " + message[current_state] + ") ")

				current_state = oth[current_state]
				#print("-> " + str(current_state))
				if current_state == -1:
					current_state = 0
					current_string = ""

			if current_state == 11:
				in_comment_line = True
				if not in_comment:
					last_comment_line = tk_counter

			if current_state == 13:
				in_comment_all = True
				if not in_comment:
					last_comment_line = tk_counter

			if term[current_state]:
				if have_star[current_state]:
					fin = False
					current_string = current_string[0: -1]

				if current_state == 2:
					flag = False
					for s in symbols_list:
						if s == current_string:
							flag = True

					if not is_in_keyword(current_string) and not flag:
						symbols_list.append(current_string)

					if is_in_keyword(current_string):
						if not line_number_printed:
							if TFL:
								TK.write("\n")
							if not TFL:
								TFL = True
							TK.write(str(tk_counter) + ".\t")
							line_number_printed = True
						if tk_sh:
							TK.write(' ')
						if not tk_sh:
							tk_sh = True

						TK.write("(KEYWORD, " + current_string + ")")
					else:
						if not line_number_printed:
							if TFL:
								TK.write("\n")
							if not TFL:
								TFL = True

							TK.write(str(tk_counter) + ".\t")
							line_number_printed = True

						if tk_sh:
							TK.write(' ')
						if not tk_sh:
							tk_sh = True

						TK.write("(ID, " + current_string + ")")

				elif current_state == 4:
					if not line_number_printed:
						if TFL:
							TK.write("\n")
						if not TFL:
							TFL = True
						TK.write(str(tk_counter) + ".\t")
						line_number_printed = True

					if tk_sh:
						TK.write(' ')
					if not tk_sh:
						tk_sh = True

					TK.write("(NUM, " + current_string + ")")
				elif current_state == 5 or current_state == 7 or current_state == 9:
					if not line_number_printed:
						if TFL:
							TK.write("\n")
						if not TFL:
							TFL = True
						TK.write(str(tk_counter) + ".\t")
						line_number_printed = True

					if tk_sh:
						TK.write(' ')
					if not tk_sh:
						tk_sh = True

					TK.write("(SYMBOL, " + current_string + ")")

				elif current_state == 12:
					in_comment_all = False
					in_comment_line = False

				current_state = 0
				current_string = ""


if current_state == 11 or current_state == 13:
	lexical_errors[last_comment_line].append("(" + current_string[:7] + "..., " + "Unclosed comment) ")

LFL = False
for i in range(1000):
	if len(lexical_errors[i]) > 0:
		if LFL:
			LE.write("\n")
		if not LFL:
			LFL = True

		LE.write(str(i) + ".\t")

		sh = False
		for s in lexical_errors[i]:
			if sh:
				LE.write(' ')
			if not sh:
				sh = True
			LE.write(s[0: -1])

if not LFL:
	LE.write("There is no lexical error.")

for s in symbols_list:
	if st_counter > 0:
		ST.write("\n")
	st_counter += 1
	#   print(str(st_counter) + ".\t" + s)
	ST.write(str(st_counter) + ".\t" + s)

ST.close()
LE.close()
TK.close()
INP.close()
