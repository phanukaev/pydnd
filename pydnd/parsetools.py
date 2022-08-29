def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def is_mod_literal(string):
    string = delete_whitespace(string)
    return string.startswith(('+', '-')) and is_int(string)

def words(string):
    return string.split()

def unwords(lst):
    return ' '.join(lst)

def lines(string):
    return string.split('\n')

def unlines(lst):
    stripped = map(lambda x : x.strip(), lst)
    return '\n'.join(stripped)

def first_word(string):
    first_and_rest = string.split(maxsplit = 1)
    if len(first_and_rest) == 1:
        first, rest = string, ''
    else:
        first, rest = first_and_rest
    return first, rest

def last_word(string):
    body, tail = string.rsplit(maxsplit = 1)
    return body, tail

def first_line(string):
    first_and_rest = string.split('\n', maxsplit = 1)
    if len(first_and_rest) == 1:
        first, rest = string, ''
    else:
        first, rest = first_and_rest
    return first, rest

def delete_whitespace(string):
    return ''.join(words(string))

def is_math(string):
    # this function is bad
    allowed_chars = {str(i) for i in range(10)} | {'+','-','*','/','(',')'}
    chars = set(delete_whitespace(string))

    return chars.issubset(allowed_chars) 

def expand(string, expandables):
    for k, f in expandables.items():
        if string.find(k) != -1:
            string = string.replace(k, str( f() ))

    return string

def is_expr(string, expandables = {}):
    return is_math(expand(string, expandables))

def eval_expr(string, expandables = {}):
    if is_expr(string):
        return(eval(expand(string, expandables)))
    else:
        return string

def proc_all_math(string):
    while (openbrack := string.find('[')) != -1:
        if openbrack < (closebrack := string.find(']')) != -1:
            mathblock = string[openbrack+1:closebrack]
            mathblock = str(eval_expr(mathblock))
            string = string[:openbrack] + mathblock + string[closebrack + 1:]
        else:
            break
    return string


