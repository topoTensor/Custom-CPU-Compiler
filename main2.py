test_text = """

    x = (2 +3)* 4 + sin(a)

    func alo(x,y) {
        if ( ( x +y) *z < 3) {
            z= 3 *3
    }

    

"""

class Token:
    # operator: like +,-,*,/,=
    # word: either variables like x, alo, or numbers

    def __init__(self, typ, val):
        self.typ = typ
        self.val = val
    
    def __repr__(self):
        return f"(type : {self.typ}, value : {repr(self.val)})"
    
def clean(txt):
    while len(txt) != 0 and (txt[0] == ' ' or txt[0] == '\n'):
        txt = txt[1:]
        
    while len(txt) != 0 and (txt[-1] == ' ' or txt[-1] == '\n'):
        txt = txt[:-1]

    return txt


def sequence_into_tokens(sequence, typ='arguments'):
    # arguments - for function declaration
    # expr - for function evaluation
    i =0 
    tokens = []
    read_j = -1

    while i <= len(sequence):
        word, read_j = read_till(sequence[i:], ',')
        tokens.append(Token(typ, clean(word)))
        i += read_j
        # print(repr(word),"|",read_j, i,"|", repr(sequence), repr(clean(sequence)), "|",len(sequence))

    return tokens

def read_till(text, symbol):
    j =0 
    while j < len(text):
        if text[j] == symbol:
            break
        j+=1

    # notice that if j == len(text) then it couldn't find the symbol
    # it truncates the symbol
    return (text[:j], j+1)

# ! MAKE NORMAL ERROR HANDLING
def read_bracket_till(text, opener, closer):
    j =0 
    openers = 0
    closers = 0
    while j < len(text):
        if text[j] == opener:
            openers+=1
        if text[j] == closer:
            closers += 1
        
        j+=1
        if closers == openers and text[j] == closer:
            break

    if opener > closer:
        raise Exception( f"couldn't find the bracket type {closer} for {opener}")

    # notice that if j == len(text) then it couldn't find the symbol
    # it truncates the symbol
    return (text[:j], j+1)


class Lexer:

    def __init__(self, text):
        self.tokens = []
        self.i = 0
        self.text = text
        self.cursor = ''
    
    def define_func(self):
        func_name, read_j = read_till(self.text[self.i+1:], '(')
        if read_j == len(self.text[self.i:]):
            raise EnvironmentError(f"couldn't find left parenth in function {func_name} declaration")
        self.tokens.append(Token('function', func_name))

        self.i += read_j

        sequence, read_j = read_till(self.text[self.i+1:], ')')
        if read_j == len(self.text[self.i:]):
            raise EnvironmentError(f"couldn't find right parenth in function {func_name} declaration")
        self.tokens.extend(sequence_into_tokens(sequence, 'arguments'))
        
        self.i += read_j

        _, read_j = read_till(self.text[self.i+1:], '{')
        if read_j == len(self.text[self.i:]):
            raise EnvironmentError(f"couldn't find left bracket in function {func_name} declaration")
            
        self.i += read_j
        
        body, read_j = read_bracket_till(self.text[self.i+1:], '{', '}')
        if read_j == len(self.text[self.i:]):
            raise EnvironmentError(f"couldn't find left bracket in function {func_name} declaration")
        
        self.i += read_j
        
        self.tokens.append(Token("start function", "{"))
        body_lexer = Lexer(body)
        self.tokens.extend(body_lexer.lex())
        self.tokens.append(Token("end function", "}"))

        self.cursor = ''

    def define_if(self):
        _, read_j = read_till(self.text[self.i+1:], '(')
        if read_j == len(self.text[self.i:]):
            raise EnvironmentError(f"couldn't find left parenth in if statement")

        self.i += read_j

        condtion, read_j = read_bracket_till(self.text[self.i+1:], '(', ')')
        if read_j == len(self.text[self.i:]):
            raise EnvironmentError(f"couldn't find right parenth in if statement")
        self.tokens.extend(sequence_into_tokens(condtion, 'condition'))
        
        self.i += read_j

        _, read_j = read_till(self.text[self.i+1:], '{')
        if read_j == len(self.text[self.i:]):
            raise EnvironmentError(f"couldn't find left bracket in if statement")
            
        self.i += read_j
        
        body, read_j = read_till(self.text[self.i+1:], '}')
        if read_j == len(self.text[self.i:]):
            raise EnvironmentError(f"couldn't find left bracket in if statement")
        
        self.tokens.append(Token("start if", "{"))
        body_lexer = Lexer(body)
        self.tokens.extend(body_lexer.lex())
        self.tokens.append(Token("end if", "}"))

        self.i += read_j
        self.cursor = ''

    def lex(self):

        while True:
            if self.i >= len(self.text):
                break
            
            elif self.text[self.i] == '=':
                self.tokens.append(Token('var', clean(self.cursor)))
                right_part, read_j = read_till(self.text[self.i+1:], '\n')
                self.tokens.append(Token('expr', clean(right_part)))
                self.i += read_j
                self.cursor = ''
            
            elif clean(self.cursor) == 'func':
                self.define_func()
                self.i += 1 # }


            elif clean(self.cursor) == 'if':
                self.define_if()
                self.i += 1 # }

            self.cursor += self.text[self.i]
            self.i+=1

        return self.tokens

lexer = Lexer(test_text)
tokens = lexer.lex()
for t in tokens:
    print(t)