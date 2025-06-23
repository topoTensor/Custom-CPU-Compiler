#########################################################
#   Assembly lexer file. Created on 23/6/25
#   Intent: The main reason was to separate the lexing part of the assembly from the isa_compiler.py file. 
#           Though the syntax is trivial, there were several problems with comments and commas.
#           They were too verbose to solve in the compiler file.
#           I don't use the custom iterator object either, because it turned out to be easier to just use the split function
#           
#           The lexer supports comments, all opcodes, all registers, numerical (signed and unsigned) immediate values, hex immediate values and also labels.

import opcodes as op

# A quick wrapper around the tuple
class AssemblyToken:
    def __init__(self, token_type, value, line, word):
        self.token_type = token_type
        self.value = value
        self.line = line
        self.word = word
    
    def __repr__(self) -> str:
        return f"( {self.token_type}, {self.value}, {self.line} : {self.word} )"

# The lexer
class AssemblyLexer:
    def __init__(self, input_text: str):

        self.opcodes = [op.name for op in op.Opcode] # all possible opcodes
        self.registers = ['r'+str(i) for i in range(32)] # all possible registers (r0-r31)

        self.tokens = []

        self.text = input_text

    def pretty(self, only_value=False):
        """
        only_value - if True, prints only the token's value. i.e. ('OPCODE', add, i, j) will be printed as add. If False prints each token's type, value, line and word index.
        """

        # iterate over all tokens, print them in a 'opcode a b c' manner.
        i = 0
        end=''
        while i < len(self.tokens):
            # if the token is of type opcode, label or eof, then print a newline before them
            if i+1 < len(self.tokens) and (self.tokens[i+1].token_type in ['OPCODE', 'LABEL', 'EOF']):
                end = '\n'
            else:
                end = ' '
            
            if only_value:
                print(self.tokens[i].value, end=end)
            else:
                print(self.tokens[i], end=end)
            i+=1

    def tokenize(self):
        self.tokens = []

        # separate the newliens for easier lexing
        self.text = repr(self.text).replace('\\n', " __TOKENIZATION__NEW__LINE ")[1:-1]

        # split into word and symbols
        split = self.text.split()

        i = 0
        line = 0
        word = 0
        while i < len(split):
            s = split[i]

            # keep track of the line and word
            if s == "__TOKENIZATION__NEW__LINE":
                line += 1
                word = 0

            # if a label declaration. e.g. 'label:'
            elif s[-1] == ':':
                self.tokens.append(AssemblyToken("LABEL", s[:-1], line, word))

            # if opcode
            elif s.upper() in self.opcodes:
                self.tokens.append(AssemblyToken("OPCODE", s, line, word))

            # if register with comma. e.g. 'r0,'
            elif s[:-1].lower() in self.registers:
                self.tokens.append(AssemblyToken("REGISTER", s[:-1], line, word))
            
            # if register without comma. e.g. 'r0'
            elif s.lower() in self.registers:
                self.tokens.append(AssemblyToken("REGISTER", s, line, word))
            
            # if a number
            elif str.isnumeric(s):
                self.tokens.append(AssemblyToken("NUMERIC", s, line, word))

            # if a number with unary minus. e.g. '-10'
            elif s[0] == '-' and str.isnumeric(s[1:]):
                self.tokens.append(AssemblyToken("SIGNED", s, line, word))
            
            # if a hexidecimal
            elif s[:2] == '0x':
                self.tokens.append(AssemblyToken("HEX", s, line, word))
            
            # if a comment. Traverse the whole line till the newline word
            elif ';' in s:
                while s != '__TOKENIZATION__NEW__LINE':
                    if i+1 >= len(split):
                        break
                    i += 1
                    s = split[i]
                line += 1
                word = 0

            else:
                # ignore commas. It can happen if the line was written 'operator r0 , r1' and the comma got separated.
                if s != ',':
                    # otherwise, it's either a label as in 'j label', or a junk word. The second case must be handled by parser.
                    self.tokens.append(AssemblyToken("IDENTIFIER", s, line, word))

            i += 1
            word += 1

        self.tokens.append(AssemblyToken("EOF",0,line, word))
        return self.tokens
    

# just for future testing. A redundant part. Should be removed after everything's done.
TESTING = False
if TESTING:
    with open("test_input", "r") as file:
        test_text = file.read()

        lexer = AssemblyLexer(test_text)
        lexer.tokenize()
        lexer.pretty()