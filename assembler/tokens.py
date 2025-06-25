#########################################################
#   Tokens class. Created on 22/6/25
#   Intent: The wrapper for (token_type, token_value, line, column) tuples. Class Tokens is an enum with all possible token types.
#           OPERATORS, NUMBERS, KEYWORDS and PUNCTUATION incldue all possible characters of that type. Note that
#           multi-character operations should be handled by the lexer. For now, maximum length of multi-character operators is 2.
#
#           Note that lines and columns start with 1

from enum import Enum

OPERATORS = ['+', '-', '*', '/', '=', '<', '>']
NUMBERS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
KEYWORDS = ['if', 'while', 'function', 'return']
PUNCTUATIONS = [',', '(', ')', '{', '}', '[', ']']

class Tokens(Enum):
    IDENTIFIER =0
    KEYWORD =1
    NUMBER =2
    OPERATOR =3
    PUNCTUATION =4
    EOF=5

class Token:
    def __init__(self, token_type, value, line, column):
        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self) -> str:
        return f"( {repr(self.token_type)}, {repr(self.value)}, {self.line}, {self.column} )"
    
    def compare(self, t2):
        """ Returns a 4 tuple of bool values, whether token_type, value, line and column match. """
        return (self.token_type == t2.token_type, self.value == t2.value, self.line == t2.line, self.column == t2.column)