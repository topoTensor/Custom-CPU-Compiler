from tokens import Token, Tokens
from lexer import Lexer
from parser import Parser
from abstract_syntax_tree import AST
import parser2

class LexerTester:
    """
        Tester class for lexer. Run test function to check if the dummy input gets lexed correctly.  
        Note, it ignores lines and columns index.
    """
    def test(self):

        test_text = """
__init__ = 7
_var123abc = 12abc34
important
valid_name = true123
42isTheAnswer
= == = != !== <= << >> >= >=>
weirddots = 314
unclosed string
if (not_hello   ==) {
delete qweqweq
}
else if {
} not else{
}
        """

        test_expect = [
        Token( Tokens.IDENTIFIER, '__init__', 1, 1 ),
        Token( Tokens.OPERATOR, '=', 1, 10 ),
        Token( Tokens.NUMBER, 7, 1, 12 ),
        Token( Tokens.IDENTIFIER, '_var', 2, 1 ),
        Token( Tokens.NUMBER, 123, 2, 5 ),
        Token( Tokens.IDENTIFIER, 'abc', 2, 8 ),
        Token( Tokens.OPERATOR, '=', 2, 12 ),
        Token( Tokens.NUMBER, 12, 2, 14 ),
        Token( Tokens.IDENTIFIER, 'abc', 2, 16 ),
        Token( Tokens.NUMBER, 34, 2, 19 ),
        Token( Tokens.IDENTIFIER, 'important', 3, 1 ),
        Token( Tokens.IDENTIFIER, 'valid_name', 4, 1 ),
        Token( Tokens.OPERATOR, '=', 4, 12 ),
        Token( Tokens.IDENTIFIER, 'true', 4, 14 ),
        Token( Tokens.NUMBER, 123, 4, 18 ),
        Token( Tokens.NUMBER, 42, 5, 1 ),
        Token( Tokens.IDENTIFIER, 'isTheAnswer', 5, 3 ),
        Token( Tokens.OPERATOR, '=', 6, 1 ),
        Token( Tokens.OPERATOR, '==', 6, 3 ),
        Token( Tokens.OPERATOR, '=', 6, 6 ),
        Token( Tokens.OPERATOR, '!=', 6, 8 ),
        Token( Tokens.OPERATOR, '!=', 6, 11 ),
        Token( Tokens.OPERATOR, '=', 6, 13 ),
        Token( Tokens.OPERATOR, '<=', 6, 15 ),
        Token( Tokens.OPERATOR, '<', 6, 18 ),
        Token( Tokens.OPERATOR, '<', 6, 19 ),
        Token( Tokens.OPERATOR, '>', 6, 21 ),
        Token( Tokens.OPERATOR, '>', 6, 22 ),
        Token( Tokens.OPERATOR, '>=', 6, 24 ),
        Token( Tokens.OPERATOR, '>=', 6, 27 ),
        Token( Tokens.OPERATOR, '>', 6, 29 ),
        Token( Tokens.IDENTIFIER, 'weirddots', 7, 1 ),
        Token( Tokens.OPERATOR, '=', 7, 11 ),
        Token( Tokens.NUMBER, 314, 7, 13 ),
        Token( Tokens.IDENTIFIER, 'unclosed', 8, 1 ),
        Token( Tokens.IDENTIFIER, 'string', 8, 10 ),
        Token( Tokens.KEYWORD, 'if', 9, 1 ),
        Token( Tokens.PUNCTUATION, '(', 9, 4 ),
        Token( Tokens.IDENTIFIER, 'not_hello', 9, 5 ),
        Token( Tokens.OPERATOR, '==', 9, 17 ),
        Token( Tokens.PUNCTUATION, ')', 9, 19 ),
        Token( Tokens.PUNCTUATION, '{', 9, 21 ),
        Token( Tokens.IDENTIFIER, 'delete', 10, 5 ),
        Token( Tokens.IDENTIFIER, 'qweqweq', 10, 12 ),
        Token( Tokens.PUNCTUATION, '}', 11, 25 ),
        Token( Tokens.IDENTIFIER, 'else', 12, 25 ),
        Token( Tokens.KEYWORD, 'if', 12, 30 ),
        Token( Tokens.PUNCTUATION, '{', 12, 33 ),
        Token( Tokens.PUNCTUATION, '}', 13, 5 ),
        Token( Tokens.IDENTIFIER, 'not', 13, 7 ),
        Token( Tokens.IDENTIFIER, 'else', 13, 11 ),
        Token( Tokens.PUNCTUATION, '{', 13, 15 ),
        Token( Tokens.PUNCTUATION, '}', 14, 25 ),
        Token( Tokens.EOF, 'EOF', 14, 25 )]


        lexer = Lexer(test_text , testing=True)
        tokens = lexer.tokenize()
        failed = False

        for j,t in enumerate(tokens):
            # ignore lines and columns
            if False in t.compare(test_expect[j])[:2]:
                print(f"Lexer: token {j} doesn't match: ", t, test_expect[j], t.compare(test_expect[j]))
                failed = True 
        if not failed:
            print("\n ________ LEXER passed the test successfully ________ \n ")


class ParserTester:
    """
        Tester class for parser. Run test function to check if the dummy tokens get parsed correctly
    """
    def test(self):
        # (2 + 3) + (4 / 5 + 2 * 2 *(2 + 1))
        test_tokens = [Token( Tokens.PUNCTUATION, '(', 0, 1 ), Token( Tokens.NUMBER, 2, 0, 2 ), Token( Tokens.OPERATOR, '+', 0, 4 ), Token( Tokens.NUMBER, 3, 0, 6 ), Token( Tokens.PUNCTUATION, ')', 0, 7 ), Token( Tokens.OPERATOR, '+', 0, 9 ), Token( Tokens.PUNCTUATION, '(', 0, 11 ), Token( Tokens.NUMBER, 4, 0, 12 ), Token( Tokens.OPERATOR, '/', 0, 14 ), Token( Tokens.NUMBER, 5, 0, 16 ), Token( Tokens.OPERATOR, '+', 0, 18 ), Token( Tokens.NUMBER, 2, 0, 20 ), Token( Tokens.OPERATOR, '*', 0, 22 ), Token( Tokens.NUMBER, 2, 0, 24 ), Token( Tokens.OPERATOR, '*', 0, 26 ), Token( Tokens.PUNCTUATION, '(', 0, 27 ), Token( Tokens.NUMBER, 2, 0, 28 ), Token( Tokens.OPERATOR, '+', 0, 30 ), Token( Tokens.NUMBER, 1, 0, 32 ), Token( Tokens.PUNCTUATION, ')', 0, 33 ), Token( Tokens.PUNCTUATION, ')', 0, 34 ), Token( Tokens.EOF, 'EOF', 0, 35 )]

        parser = Parser(test_tokens)
        ast = parser.parse()
        ast.pretty()


class Parser2Tester:
    """
        Temporary parser2 tester.
    """
    def test(self):

        test_raw_inputs = [
" (1 + 2) * (3 + 4 * (5 - 6 / (7 + 8))) - 9",
                
"-(1 + 2 * (3 - 4 / (5 + 6 * (7 - 8)))) + 9 / (10 - (11 + 12))",

"((1 + (2 - 3)) * (4 / (5 + (6 * (7 - 8))))) - (-9 + 10)",

"-( - ( (1 + 2) * (3 - 4) ) + (5 - (6 + 7 * (8 / 9))) )",

"(((((1))))) + (-2 * (3 + (-4 / (5 - 6)))) - 7",

"1 + 2 * 3 - 4 / (5 + (6 - (7 * (8 + (-9))))) + -(10 - 11)",
                           ]
        
        answers = [
' ( ( (1 + 2)  *  (3 +  (4 *  (5 -  (6 /  (7 + 8) ) ) ) ) )  - 9) ',

" ( (None -u  (1 +  (2 *  (3 -  (4 /  (5 +  (6 *  (7 - 8) ) ) ) ) ) ) )  +  (9 /  (10 -  (11 + 12) ) ) ) ",


" ( ( (1 +  (2 - 3) )  *  (4 /  (5 +  (6 *  (7 - 8) ) ) ) )  -  ( (None -u 9)  + 10) ) ",


" (None -u  ( (None -u  ( (1 + 2)  *  (3 - 4) ) )  +  (5 -  (6 +  (7 *  (8 / 9) ) ) ) ) ) ",


" ( (1 +  ( (None -u 2)  *  (3 +  ( (None -u 4)  /  (5 - 6) ) ) ) )  - 7) ",


" ( ( (1 +  (2 * 3) )  -  (4 /  (5 +  (6 -  (7 *  (8 +  (None -u 9) ) ) ) ) ) )  +  (None -u  (10 - 11) ) ) ",
        ]

        failed = False
        for i in range(len(test_raw_inputs)):
            l = Lexer(test_raw_inputs[i])
            test_tokens = l.tokenize()

            parser = parser2.Parser2()
            ast = parser.parse(test_tokens)
            q=repr(ast)
            if q != answers[i]:
                print(f"PARSER 2: failed representation test {i}. {test_raw_inputs[i]}")
                failed = True
        
        if not failed:
            print("Parser 2: All representation tests are done correctly")

class Tester:
    def __init__(self, test_lex=False, test_pars=False):
        self.test_lex = test_lex
        self.test_pars = test_pars

    def do_tests(self):
        if self.test_lex:
            lex_tester = LexerTester()
            lex_tester.test()
            
        if self.test_pars:
            pars_tester = ParserTester()
            pars_tester.test()


# parser2_tester = Parser2Tester()
# parser2_tester.test()

a = " while (x < 2) {x=3;}"

l = Lexer(a)
test_tokens = l.tokenize()

parser = parser2.Parser2()
ast = parser.parse(test_tokens)
print(ast)