# Expression file. Created on 22/6.
# Intent: Wrapper around (lhs,op,rhs) or (atomic) type of expressions for parser.
#         Though that's not the best design, it works fine for now. 
#         Note that op and rhs can be None. Op is always a token. Rhs can be a token or Expression

class Expression:
    """
    Wrapper around (lhs, op, rhs) tuple. Can be either an Expression or an Atomic.  
    Atomic is the special case, where there's no operator. In that case, lhs is the only element which is not None.
    Note that op is supposed to be token. Rhs can be a token or expression.
    """
    def __init__(self, lhs, op=None, rhs=None, atomic=False):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs
        self.atomic = atomic

    def __repr__(self) -> str:
        if self.atomic:
            return f"( Atomic {self.lhs} )"
        else:
            return f"( Expression {self.lhs} {self.op} {self.rhs} )"
        
    def pretty(self, indent=0):
        if hasattr(self.lhs, 'value'):
            print("  " * (indent+1), self.lhs.value)
        else:
            self.lhs.pretty(indent+1)

        if hasattr(self.op, 'value'):
            print("  " * indent, self.op.value)

        if hasattr(self.rhs, 'value'):
            print("  " * (indent+1), self.rhs.value)
        elif self.rhs != None:
            self.rhs.pretty(indent)