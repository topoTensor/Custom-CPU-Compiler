#########################################################
#   Assembly lexer file. Created on 23/6/25
#   Intent: The main reason was to separate the lexing part of the assembly from the isa_compiler.py file. 
#           Though the syntax is trivial, there were several problems with comments and commas.
#           They were too verbose to solve in the compiler file.
#           I don't use the custom iterator object either, because it turned out to be easier to just use the split function
#           
#           The lexer supports comments, all opcodes, all registers, numerical (signed and unsigned) immediate values, hex immediate values and also labels.

import opcodes as op
from tokens import Token

# TODO: write a better test. Compare the tokens with desired output.

# The lexer
class AssemblyLexer:
    def __init__(self, ):

        self.opcodes = [op.name for op in op.Opcode] # all possible opcodes
        self.registers = ['r'+str(i) for i in range(32)] # all possible registers (r0-r31)

        self.tokens = []

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

    def tokenize(self, input_text:str):
        # The idea is to split the text into preprocessed tokens. We suppose that the program is written syntatically correct,
        # and it allows us to split 'addi r0, r1, r2' into 'addi', 'r0', 'r1', 'r2', just using whitespace.
        # In the case that whitespace is not mandatory as with commas and columns, we add it artificially.
        # This approach is more elegant than iteration and suits better for simple syntax languages like our assembler.
        self.text = input_text
        self.tokens = []

        # Preprocess text for simple lexing, avoiding cases like 'label:' vs 'label :'
        text = self.text.replace(';', ' ; ')
        text = text.replace(':', ' : ')
        text = text.replace(',', ' ')
        text = text.replace('\n', ' __TOKENIZATION__NEW__LINE__ ')

        words = text.split()
        i = 0
        line = 1
        word = 1

        while i < len(words):
            s = words[i]

            # thrack lines
            if s == '__TOKENIZATION__NEW__LINE__':
                line += 1
                word = 0

            # labels
            elif i + 1 < len(words) and words[i + 1] == ':':
                self.tokens.append(Token("LABEL", s, line, word))
                i += 1  # Skip the ':'

            # opcodes
            elif s.upper() in self.opcodes:
                self.tokens.append(Token("OPCODE", s.upper(), line, word))

            #  registers
            elif s.lower() in self.registers:
                self.tokens.append(Token("REGISTER", s.lower(), line, word))

            # unsigned numbers
            elif s.isdigit():
                self.tokens.append(Token("NUMERIC", s, line, word))

            # signed numbers
            elif s.startswith('-') and s[1:].isdigit():
                self.tokens.append(Token("SIGNED", s, line, word))

            # hex
            elif s.startswith('0x'):
                self.tokens.append(Token("HEX", s.upper(), line, word))

            # comments
            elif s == ';':
                # Skip all words until newline
                while i < len(words) and words[i] != '__TOKENIZATION__NEW__LINE__':
                    i += 1
                line += 1
                word = 0

            # identifiers. Either syntatically incorrect words, or label jumps e.g. 'j label'. The first case must be handled by parser.
            else:
                self.tokens.append(Token("IDENTIFIER", s, line, word))

            # iterate
            i += 1
            word += 1

        # add eof. End of lexing.
        self.tokens.append(Token("EOF", 0, line, word))
        return self.tokens


# just for future testing. A redundant part. Should be removed after everything's done.
TESTING = False
if TESTING:
    programs = [
        """
        start : 
            lli   r1 ,  5
            add r2,r0, r1
            addi r1, r0,0x123
        """,
    ]
    answers = [
        [   Token( 'LABEL', 'start', 2 , 1 ), 
            Token( 'OPCODE', 'LLI', 3 , 1 ), Token( 'REGISTER', 'r1', 3 , 2 ), Token( 'NUMERIC', '5', 3 , 3 ), 
            Token( 'OPCODE', 'ADD', 4 , 1 ), Token( 'REGISTER', 'r2', 4 , 2 ), Token( 'REGISTER', 'r0', 4 , 3 ), Token( 'REGISTER', 'r1', 4 , 4 ),
            Token( 'OPCODE', 'ADDI', 5 , 1 ), Token( 'REGISTER', 'r1', 5 , 2 ), Token( 'REGISTER', 'r0', 5 , 3 ), Token( 'HEX', '0X123', 5 , 4 ),
            Token( 'EOF', 0, 6 , 1 )],
    ]

    lexer = AssemblyLexer()

    for i in range(len(programs)):
        tokens = lexer.tokenize(programs[i])
        failed = False
        for j,t in enumerate(tokens):
            if False in t.compare(answers[i][j]):
                print(f"AssemblyLexer: program {i}. token {j} doesn't match: ", t, answers[i][j], t.compare(answers[i][j]))
                failed = True
        
        if failed:
            break
        print(f"\nASSEMBLYLEXER: TEST {i} PASSED.\n")

    # with open("test_input.asm", "r") as file:
    #     test_text = file.read()

    #     lexer = AssemblyLexer(test_text)
    #     lexer.tokenize()
    #     lexer.pretty()