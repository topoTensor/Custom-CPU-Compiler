#########################################################
#   Parser file. Created on 22/6/25
#   Intent: Second step in the compiler. Uses Pratt's algorithm to make the abstract syntax tree.
#           Note that tokens should be created using lexer.py Lexer class.

# # note for 22/6. For now I will work on simple mathematical expressions. Keywords will be worked later

from tokens import Token, Tokens, OPERATORS, KEYWORDS, PUNCTUATIONS, NUMBERS
from high_language_compiler.iterator import Iterator
from expression import Expression

# TODO: note the TDD design. Write the tests.

TESTING = True

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens

        self.b_powers = {"+" : (1, 1.1), "-": (1,1.1), "*":(2,2.1), "/":(2,2.1)}

    def parse(self):
        self.iterator = Iterator(self.tokens, 'Parser_iterator')
        return self.parse_expression()

    def parse_expression(self, min_bp=0.0) -> Expression:
        # NOTE: if you don't understand how it works to the fullest, then it's just useless.
   
        lhs = self.iterator.word
        self.iterator.advance()
        if lhs.value == '(':
            lhs = self.parse_expression(0.0)
            
            if self.iterator.word.value != ")":
                raise SyntaxError("expected closing parenth")

            self.iterator.advance()

        if self.iterator.word.token_type == Tokens.EOF:
            return Expression(lhs, atomic=True)
        
        while True:
            op = self.iterator.word

            if op.token_type == Tokens.EOF:
                break

            if op.value == ')':
                return Expression(lhs, atomic=True)

            if op.value not in ['+', '-', '*', '/']:
                raise SyntaxError(f"op should be an arithmetic symbol, op: {op}")

            l_bp, r_bp = self.b_powers[op.value]
            if l_bp < min_bp:
                break

            self.iterator.advance()
            rhs = self.parse_expression(r_bp)
            lhs = Expression(lhs, op, rhs)

        return lhs


if TESTING:
    import lexer
    import textwrap

    test_text = textwrap.dedent("""
        (2 + 3) + (4 / 5 + 2 * 2 *(2 + 1))
""")

    lexer=lexer.Lexer(test_text, False)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    ast.pretty()