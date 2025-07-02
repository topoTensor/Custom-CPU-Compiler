#   Date: 28/6. It's been 6 days since the lexer was started.
#   IDK to be honest. The tree is very poorely written and I am starting to get tired of this project. I guess I should let it for
#       some time. If I am going to make something, then it should be done good. I will come back to this later.
#   I should make it easier to navigate the tree. Ideally, I need some way to extract the operation, check its validity,
#       get the left and right handsides, traverse and do the analysis on the lhs, do the same on rhs and go up to the parent and repeat.

#   Right now I had the idea to make the tree a bit simpler to traverse, but then gpt helped me to 'decode' in during the traversal.
#   Idk if it's a good idea. 

class Semantic_Analyser:
    def __init__(self):
        self.operations = []

    def tuplify_ast(self, ast):
        """
            Turns AST format into simpler tuples.
        """
        an = self.recursive_tuplify(ast)
        return an
    
    def recursive_tuplify(self, ast_or_token):
        if ast_or_token == None or isinstance(ast_or_token, list):
            return ast_or_token
        
        if hasattr(ast_or_token, 'value'):
            return ast_or_token.value
        elif ast_or_token.op == None:
            return self.recursive_tuplify(ast_or_token.lhs)
        else:
            return (ast_or_token.op.value, self.recursive_tuplify(ast_or_token.lhs), self.recursive_tuplify(ast_or_token.rhs))
        

    def analyse(self, ast):
        tuples = self.tuplify_ast(ast)
        print(tuples)
        self.my_traverse(tuples)
        print(self.operations)
        
    # I am tired

    def my_traverse(self, node):
        if isinstance(node, tuple):
            head = node[0]

            if head == '=':
                self.operations.append(f"Assign {node[1]} =")
                self.my_traverse(node[2])

            elif head in ['+', '-', '*', '/', '<', '>', '!', '&', '|', '^']:
                self.operations.append(f"Op {head}")
                self.my_traverse(node[1])
                self.my_traverse(node[2])

            elif head == 'if':
                self.operations.append("If condition:")
                self.my_traverse(node[1])
                self.operations.append("Then:")
                self.my_traverse(node[2])
                if len(node) > 3:
                    self.operations.append("Else:")
                    self.my_traverse(node[3])

            elif head == ';':
                for expr in node[1:]:
                    self.my_traverse(expr)  # No need to prepend "Next statement" unless for debug

            elif head == 'return':
                self.operations.append("Return:")
                self.my_traverse(node[1])

            elif head == 'function':
                name, params, body = node[1], node[2], node[3]
                self.operations.append(f"Function {name} with params {params}")
                self.my_traverse(body)

            else:
                # Try to detect a function declaration of the form ('hello', ...)
                if isinstance(head, str) and node[1:3] and isinstance(node[1], list):
                    # Probable function-like
                    name, params, body = node[0], node[1], node[2]
                    self.operations.append(f"Function {name} with params {params}")
                    self.my_traverse(body)
                else:
                    self.operations.append(f"Unknown tuple head: {head}")
        else:
            self.operations.append(f"Literal/Variable: {node}")
