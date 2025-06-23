#########################################################
#   Lexer file. Created on 22/6/25
#   Intent: First step in the compiler. Initiate Lexer class with raw input string, which is supposed to be the code text.
#           It will return a list of tokens, which should be given to the parser in the next compiling stage. Each token
#           can be either number, operator, punctuation, keyword or identifier. 
#
#           For now, only integers are supported. Keywords include 'if', 'while', 'function', 'retrun'
#
#           Handles multi-character operators: ==, !=, <=, >=, as well as single character operators: +, -, *, /, =
#
#           Comments are assumed to start with hashtag '#', so the string after # will be ignored.
#
#           For more, look at the tokens.py file, which is responsible for the Token class and possible token types.
#

#   The todo part is not yet included, because the language will change substantially. Most probably, in the future the lexer will
#   also support floating points, strings and arrays.

import textwrap
from tokens import Token, Tokens, OPERATORS, KEYWORDS, PUNCTUATIONS, NUMBERS

TESTING = False

class Lexer:
    """
    public functions:   
    tokenize - tokenizes the text given at class initiation.  
    add_token - adds a token to the lexer's tokens list
    """
    def __init__(self, text : str, testing=False, add_EOF=True):
        self.text = text
        self.cursor = 0
        self.tokens = []
        if len(text) == 0:
            print("WARNING: Input file is empty")
            self.char = ''
        else:
            self.char = self.text[0]

        self.line, self.column = 0,0  # for now, used only in error reporting

        self.testing = testing # whether to print the tokens and strings at the end of tokenize function
        self.add_EOF = add_EOF # whether to include the EOF token in the end of tokens list. 

    # adds a token to the self.tokens list
    def add_token(self, token_type, value):
        self.tokens.append(Token(token_type, value, self.line, self.column))

    def tokenize(self):
        # in case of empty input string
        if len(self.text) == 0:
            if self.add_EOF:
                return [Token(Tokens.EOF, '', 0,0)]
            else:
                return []

        # look for all possible token types. advance one step each iteration till the end of the text
        while self._can_peek():

            # update lines and columns counters
            if self.char == '\n':
                self.line += 1
                self.column = 0
            else:
                self.column += 1

            # white space
            if self._is_white_space():
                self._advance()
                continue

            elif self.char == '#':
                while self._peek() != '\n':
                    self._advance()

            # operators
            elif self.char in OPERATORS:
                self._add_operator()

            # numbers
            elif self.char in NUMBERS:
                self._add_number()

            # punctuation
            elif self.char in PUNCTUATIONS:
                self.add_token(Tokens.PUNCTUATION, self.char)

            # keywords and identifiers
            elif self.char.isalpha() or self.char == '_':
                self._add_keyword_identifier()

            else:
                raise SyntaxError(f"Invalid character '{self.char}' at line {self.line}, column {self.column}")


            # advance one step
            if self._can_peek():
                self._advance()
            else:
                break

        # add EOF if needed
        if self.add_EOF:
            self.add_token(Tokens.EOF, 'EOF')

        # print text and tokens for testing
        if self.testing:
            print("LEXER INPUT FILE:\n",self.text)
            print("TOKENS:\n",self.tokens)

        # end of lexing
        return self.tokens
    

    def _is_white_space(self):
        return self.char == ' ' or self.char == '\n' or self.char == '\t'
    

    def _is_peek_white_space(self):
        return self._peek() == ' ' or self._peek() == '\n' or self._peek() == '\t'


    # advances the cursor one step
    def _advance(self):
        if self._can_peek():
            self.cursor += 1
            self.char = self.text[self.cursor]
            return self.char
        else:
            raise SyntaxError(f"Lexer tried to advance out-of-bounds character at position {self.cursor}")


    # returns next character, but doesn't _advance the cursor        
    def _peek(self):
        if self._can_peek():
            return self.text[self.cursor+1]
        else:
            raise SyntaxError(f"Lexer tried to peek out-of-bounds character at position {self.cursor}")


    # returns whetehr the next step leaves the text
    def _can_peek(self):
        return self.cursor+1 < len(self.text)


    # checks all possible operators and adds accordingly. Checks for ==, !=, <=, >= cases first using _peek
    def _add_operator(self):
        assert self.char in OPERATORS

        # define, is equal to
        if self.char == '=':  
            if self._can_peek() and self._peek() == '=': # check for == case
                self.add_token(Tokens.OPERATOR, '==')
                self._advance()
            else:
                self.add_token(Tokens.OPERATOR, '=')


        # not equal to
        elif self.char == '!' and self._can_peek() and self._peek() == '=':  # check for != case
            self.add_token(Tokens.OPERATOR, '!=')
            self._advance()


        # less or equal than, less than
        elif self.char == '<':
            if self._can_peek() and self._peek() == '=':  # check for <= case
                self.add_token(Tokens.OPERATOR, '<=')
                self._advance()

            else:
                self.add_token(Tokens.OPERATOR, '<')
    

        # greater or equal than, greater than
        elif self.char == '>':
            if self._can_peek() and self._peek() == '=':  # check for <= case
                self.add_token(Tokens.OPERATOR, '>=')
                self._advance()
                
            else:
                self.add_token(Tokens.OPERATOR, '>')
        

        # +,-,*,/ and so on. Note that this function doesn't get called unless self.char is in operators
        else: 
            self.add_token(Tokens.OPERATOR, self.char)

    # reads till the character is operator, number or punctuation. Adds keyword or identifier accordingly if the word is in keywords list.
    def _add_keyword_identifier(self):
        identifier = self.char
                
        while (self._can_peek()): # lex whole identifier
            if not self._is_peek_white_space() and self._peek() not in OPERATORS and self._peek() not in NUMBERS and self._peek() not in PUNCTUATIONS:
                identifier += self._advance()
            else:
                break

        if identifier in KEYWORDS:
            self.add_token(Tokens.KEYWORD, identifier)
        else:
            self.add_token(Tokens.IDENTIFIER, identifier)

    # reads the whole number and adds to tokens. Reads number by peeking, stops if the _peek is not a number anymore
    def _add_number(self):
        assert self.char in NUMBERS

        number_str = self.char
        while (self._can_peek()) and (self._peek() in NUMBERS): # traverse the whole number
            number_str += self._advance()

        self.add_token(Tokens.NUMBER, int(number_str))
        
if TESTING:

    test_text = textwrap.dedent("""
        # this is a comment

        x = 2 + 2 
        if ( x <= 1 ) {
            x = x + 1
        } 
        function hello(a,b){
            return a + b
        }
        while (hello(a,b) == x){
            x = hello(a + b)
        }
    """)

    lexer=Lexer(test_text , TESTING)
    tokens = lexer.tokenize()
    print(test_text)
    for t in tokens:
        print(t)