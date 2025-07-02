from tokens import Token, Tokens
from lexer import Lexer
from parser import Parser
from abstract_syntax_tree import AST
from semantic_analysis import Semantic_Analyser
import parser2

class LexerTester:
    """
        Tester class for lexer. Run test function to check if the dummy input gets lexed correctly.  
        Note, it ignores lines and columns index.
    """
    def test(self):

        test_text = """
abc123 = 42;
def456 = abc123 + 3;
result = myFunc1(x1, y2, 99);
"""

        test_expect =  [Token( Tokens.IDENTIFIER, 'abc123', 1, 1 ), Token( Tokens.OPERATOR, '=', 1, 8 ), Token( Tokens.NUMBER, 42, 1, 10 ), Token( Tokens.OPERATOR, ';', 1, 12 ), Token( Tokens.IDENTIFIER, 'def456', 2, 1 ), Token( Tokens.OPERATOR, '=', 2, 8 ), Token( Tokens.IDENTIFIER, 'abc123', 2, 10 ), Token( Tokens.OPERATOR, '+', 2, 17 ), Token( Tokens.NUMBER, 3, 2, 19 ), Token( Tokens.OPERATOR, ';', 2, 20 ), Token( Tokens.IDENTIFIER, 'result', 3, 1 ), Token( Tokens.OPERATOR, '=', 3, 8 ), Token( Tokens.IDENTIFIER, 'myFunc1', 3, 10 ), Token( Tokens.PUNCTUATION, '(', 3, 17 ), Token( Tokens.IDENTIFIER, 'x1', 3, 18 ), Token( Tokens.PUNCTUATION, ',', 3, 20 ), Token( Tokens.IDENTIFIER, 'y2', 3, 22 ), Token( Tokens.PUNCTUATION, ',', 3, 24 ), Token( Tokens.NUMBER, 99, 3, 26 ), Token( Tokens.PUNCTUATION, ')', 3, 28 ), Token( Tokens.OPERATOR, ';', 3, 29 ), Token( Tokens.EOF, 'EOF', 4, 0 )]


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

class SemanticTester:
    def __init__(self, ast):
        self.ast = ast
        self.analyser = Semantic_Analyser()

    def test(self):
        print(self.analyser.analyse(self.ast))


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


a = """
x=2;

if (x<2) {
   x=x+2;
}; else if (x > 2) {
   x=x+2*3;
}; else {
   x=x;
};

function hello(a,b){
   return a+b;
};
"""


l = Lexer(a)
test_tokens = l.tokenize()

# print(test_tokens)

parser = parser2.Parser2()
ast = parser.parse(test_tokens)
print(ast)

analyser = Semantic_Analyser()
analyser.analyse(ast)