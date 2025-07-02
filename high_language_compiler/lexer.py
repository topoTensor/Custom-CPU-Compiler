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

# ^ The lexer is ready.

import textwrap
from tokens import Token, Tokens, OPERATORS, KEYWORDS, PUNCTUATIONS, NUMBERS

from iterator import Iterator


class Lexer:
    """
    public functions:   
    tokenize - tokenizes the text given at class initiation.  
    _add_token - adds a token to the lexer's tokens list
    """
    def __init__(self, text : str, testing=False, add_EOF=True):
        self.text = text

        self.iterator = Iterator(text, name='high-level-lexer-iterator')

        # self.cursor = 0
        self.tokens = []
        if len(text) == 0:
            print("WARNING: Input file is empty")
            self.iterator.word = ''
        else:
            self.iterator.word = self.text[0]

        self.line, self.column = 0,0  # for now, used only in error reporting

        self.testing = testing # whether to print the tokens and strings at the end of tokenize function
        self.add_EOF = add_EOF # whether to include the EOF token in the end of tokens list. 

    def tokenize(self):
        # in case of empty input string
        if len(self.text) == 0:
            if self.add_EOF:
                return [Token(Tokens.EOF, '', 0,0)]
            else:
                return []

        # look for all possible token types. advance one step each iteration till the end of the text
        while self.iterator.cursor < len(self.text):

            # update lines and columns counters
            if self.iterator.word == '\n':
                self.line += 1
                self.column = 0
            else:
                self.column += 1

            # white space
            if self._is_white_space():
                if self.iterator.can_peek():
                    self.iterator.advance()
                else:
                    break
                continue

            elif self.iterator.word == '#':
                while self.iterator.peek() != '\n':
                    self.iterator.advance()

            # operators
            elif self.iterator.word in OPERATORS:
                self._add_operator()

            # numbers
            elif self.iterator.word in NUMBERS:
                self._add_number()

            # punctuation
            elif self.iterator.word in PUNCTUATIONS:
                self._add_token(Tokens.PUNCTUATION, self.iterator.word)

            # keywords and identifiers
            elif self.iterator.word.isalpha() or self.iterator.word == '_':
                self._add_keyword_identifier()

            else:
                raise SyntaxError(f"Invalid character '{self.iterator.word}' at line {self.line}, column {self.column}")


            # advance one step
            if self.iterator.can_peek():
                self.iterator.advance()
            else:
                break

        # add EOF if needed
        if self.add_EOF:
            self._add_token(Tokens.EOF, 'EOF')

        # print text and tokens for testing
        if self.testing:
            print("LEXER INPUT FILE:\n",self.text)
            print("TOKENS:\n",self.tokens)

        # end of lexing
        return self.tokens
    
    #
    # UTILITY FUNCTIONS ________________________________________________________________________________________________
    #

    # check for white space
    def _is_white_space(self):
        return self.iterator.word == ' ' or self.iterator.word == '\n' or self.iterator.word == '\t'

    def _is_peek_white_space(self):
        return self.iterator.peek() == ' ' or self.iterator.peek() == '\n' or self.iterator.peek() == '\t'

    # adds a token to the self.tokens list
    def _add_token(self, token_type, value):
        self.tokens.append(Token(token_type, value, self.line, self.column))
        self.column += len(str(value)) - 1  # so that words don't count as a single character


    # checks all possible operators and adds accordingly. Checks for ==, !=, <=, >= cases first using iterator.peek
    def _add_operator(self):
        assert self.iterator.word in OPERATORS

        # define, is equal to
        if self.iterator.word == '=':  
            if self.iterator.can_peek() and self.iterator.peek() == '=': # check for == case
                self._add_token(Tokens.OPERATOR, '==')
                self.iterator.advance()
            else:
                self._add_token(Tokens.OPERATOR, '=')


        # not equal to
        elif self.iterator.word == '!':
            if self.iterator.can_peek() and self.iterator.peek() == '=':
                self._add_token(Tokens.OPERATOR, '!=')
                self.iterator.advance()
            else:
                self._add_token(Tokens.OPERATOR, '!')
            

        # less or equal than, less than
        elif self.iterator.word == '<':
            if self.iterator.can_peek() and self.iterator.peek() == '=':  # check for <= case
                self._add_token(Tokens.OPERATOR, '<=')
                self.iterator.advance()
            elif self.iterator.can_peek() and self.iterator.peek() == '<':  # check for << case
                self._add_token(Tokens.OPERATOR, '<<')
                self.iterator.advance()
            else:
                self._add_token(Tokens.OPERATOR, '<')
    

        # greater or equal than, greater than
        elif self.iterator.word == '>':
            if self.iterator.can_peek() and self.iterator.peek() == '=':  # check for <= case
                self._add_token(Tokens.OPERATOR, '>=')
                self.iterator.advance()
            elif self.iterator.can_peek() and self.iterator.peek() == '>':  # check for >> case
                self._add_token(Tokens.OPERATOR, '>>')
                self.iterator.advance()
            else:
                self._add_token(Tokens.OPERATOR, '>')
        

        # +,-,*,/ and so on. Note that this function doesn't get called unless self.iterator.word is in operators
        else: 
            self._add_token(Tokens.OPERATOR, self.iterator.word)

    # reads till the character is operator, number or punctuation. Adds keyword or identifier accordingly if the word is in keywords list.
    def _add_keyword_identifier(self):
        identifier = self.iterator.word
                
        while (self.iterator.can_peek()): # lex whole identifier
            # traverse until it's either 1) white space, 2) operator, 4) punctuation
            if not self._is_peek_white_space() and self.iterator.peek() not in OPERATORS and self.iterator.peek() not in PUNCTUATIONS:
                identifier += self.iterator.advance()
            else:
                break
        
        # differentiate between keywords and identifiers
        if identifier in KEYWORDS:
            self._add_token(Tokens.KEYWORD, identifier)
        else:
            self._add_token(Tokens.IDENTIFIER, identifier)

    # reads the whole number and adds to tokens. Reads number by peeking, stops if the iterator.peek is not a number anymore
    def _add_number(self):
        assert self.iterator.word in NUMBERS

        number_str = self.iterator.word
        while (self.iterator.can_peek()) and (self.iterator.peek() in NUMBERS): # traverse the whole number
            number_str += self.iterator.advance()

        if number_str[0] == '0' and len(number_str) > 1:
            raise SyntaxError(f"Invalid number {number_str} starts with 0. At line {self.line}, column {self.column}")

        self._add_token(Tokens.NUMBER, int(number_str))
        


