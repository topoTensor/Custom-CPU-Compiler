import opcodes as op
from iterator import Iterator
from tokens import Token

class AssemblyLexer:
    def __init__(self, input_text: str):
        self.opcodes = [op.name for op in op.Opcode]  # All possible opcodes
        self.registers = [f'r{i}' for i in range(32)]  # All possible registers (r0-r31)
        self.tokens = []
        self.iterator = Iterator(input_text, 'assembly-lexer-iterator')
        self.text = input_text

    def pretty(self, only_value=False):
        """Pretty print tokens with optional simplified output"""
        output = []
        for i, token in enumerate(self.tokens):
            if only_value:
                output.append(str(token.value))
            else:
                output.append(str(token))
            # Add newline after opcodes, labels, or before EOF
            if (i + 1 < len(self.tokens) and 
                self.tokens[i+1].token_type in ['OPCODE', 'LABEL', 'EOF']):
                output.append('\n')
            else:
                output.append(' ')
        print(''.join(output).strip())

    def tokenize(self, log_output=False):
        """Main tokenization method with improved handling"""
        self.tokens = []
        line = 1
        column = 1
        current_token = ''
        
        while self.iterator.can_peek():
            char = self.iterator.word
            
            # Handle line counting
            if char == '\n':
                line += 1
                column = 1
                self.iterator.advance()
                continue
            
            # Skip whitespace
            if char in [' ', '\t']:
                self.iterator.advance()
                column += 1
                continue
            
            # Handle comments
            if char == ';':
                while self.iterator.can_peek() and self.iterator.peek() != '\n':
                    self.iterator.advance()
                self.iterator.advance()  # Skip the newline
                line += 1
                column = 1
                continue
            
            # Handle labels
            if char == ':':
                if current_token:
                    self.tokens.append(Token('LABEL', current_token + ':', line, column))
                    current_token = ''
                    self.iterator.advance()
                    column += 1
                continue
            
            # Handle registers (r0-r31)
            if char == 'r' and self.iterator.can_peek():
                reg_token = 'r'
                self.iterator.advance()
                column += 1
                
                # Collect register number
                while self.iterator.can_peek() and self.iterator.word.isdigit():
                    reg_token += self.iterator.word
                    self.iterator.advance()
                    column += 1
                
                if reg_token in self.registers:
                    self.tokens.append(Token('REGISTER', reg_token, line, column))
                else:
                    raise ValueError(f"Invalid register {reg_token} at line {line}, column {column}")
                continue
            
            # Handle hex numbers (0x...)
            if char == '0' and self.iterator.can_peek(1) and self.iterator.peek(1).lower() == 'x':
                hex_token = '0x'
                self.iterator.advance()  # Skip '0'
                self.iterator.advance()  # Skip 'x'
                column += 2
                
                # Collect hex digits
                while (self.iterator.can_peek() and 
                       self.iterator.word.lower() in '0123456789abcdef'):
                    hex_token += self.iterator.word
                    self.iterator.advance()
                    column += 1
                
                self.tokens.append(Token('HEX', hex_token, line, column))
                continue
            
            # Handle binary numbers (0b...)
            if char == '0' and self.iterator.can_peek(1) and self.iterator.peek(1).lower() == 'b':
                bin_token = '0b'
                self.iterator.advance()  # Skip '0'
                self.iterator.advance()  # Skip 'b'
                column += 2
                
                # Collect binary digits
                while self.iterator.can_peek() and self.iterator.word in '01':
                    bin_token += self.iterator.word
                    self.iterator.advance()
                    column += 1
                
                self.tokens.append(Token('BIN', bin_token, line, column))
                continue
            
            # Handle decimal numbers (including negative)
            if char.isdigit() or (char == '-' and self.iterator.can_peek(1) and 
                                self.iterator.peek(1).isdigit()):
                num_token = char
                self.iterator.advance()
                column += 1
                
                # Collect digits
                while self.iterator.can_peek() and self.iterator.word.isdigit():
                    num_token += self.iterator.word
                    self.iterator.advance()
                    column += 1
                
                # Check for valid number
                if char == '-' and len(num_token) == 1:
                    raise ValueError(f"Invalid number {num_token} at line {line}, column {column}")
                
                token_type = 'SIGNED' if char == '-' else 'NUMERIC'
                self.tokens.append(Token(token_type, num_token, line, column))
                continue
            
            # Handle opcodes
            if char.isalpha():
                current_token += char
                self.iterator.advance()
                column += 1
                
                # Check for complete opcode
                while (self.iterator.can_peek() and 
                       self.iterator.word.isalpha() and
                       (current_token + self.iterator.word).upper() in self.opcodes):
                    current_token += self.iterator.word
                    self.iterator.advance()
                    column += 1
                
                if current_token.upper() in self.opcodes:
                    self.tokens.append(Token('OPCODE', current_token.upper(), line, column))
                    current_token = ''
                continue
            
            # Handle commas (just skip them)
            if char == ',':
                self.iterator.advance()
                column += 1
                continue
            
            # Handle other characters (like symbols in labels)
            current_token += char
            self.iterator.advance()
            column += 1
        
        # Add EOF token
        self.tokens.append(Token('EOF', '', line, column))
        
        if log_output:
            print("LEXER INPUT FILE:\n", self.text)
            print("TOKENS:")
            self.pretty()
        
        return self.tokens