#########################################################
#   AST file. Created on 26/6/25
#   Intent: Class used by new parser version (made on 26/6/25). Wrapper around (lhs,op,rhs) tuple.

# TODO : handle token vs ast lhs and rhs.



class AST:
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def get_last_op(self):
        if hasattr(self.rhs, 'get_last_op') and self.rhs.op != None and self.rhs.op.value != '-u':
            return self.rhs.get_last_op()
        else:
            return self.op

    # ! NOTE: REPRESENTATION OF THE AST IS USED FOR TESTING, AS MANUALLY WRITING TREES IS TEDIOUS. CHANGE THE TESTS OUTPUTS IN CASE THE REPRESENTATION FUNCTION IS CHANGED
    def __repr__(self) ->str :

        if self.op == None:
            if hasattr(self.lhs, 'value'):
                return f"{self.lhs.value}"
            else:
                return f"{self.lhs}"
        else:
            if hasattr(self.lhs, 'value'):
                if hasattr(self.rhs, 'value'):
                    return f" ({self.lhs.value} {self.op.value} {self.rhs.value}) "
                
                return f" ({self.lhs.value} {self.op.value} {self.rhs}) "
            
            if hasattr(self.rhs, 'value'):
                return f" ({self.lhs} {self.op.value} {self.rhs.value}) "
            return f" ({self.lhs} {self.op.value} {self.rhs}) "