#########################################################
#   ISA encoder/decoder file. Created on 21/6/25
#   Intent: Created separately for the compiler project. 
#           The main purpose was to abstract the process of translating assembly into bytecode.
#           It also contains functionality for decoding the bytecode back into the assembly language.
#
#           Uses custom ISA, made by me for my custom CPU architecture.
#           For details look at the opcodes.py file, which contains details about opcodes' byte representations..

#         * For high-level details look at the 'explain_assembly' file

#           note: assembler supports comments. Comments start with ';' symbol.

# TODO: write a better test. Compare the result with desired output.


import opcodes as op
import struct

from assembly_lexer import AssemblyLexer

class ISA_compiler:
    def __init__(self):
        self.opcodes_dict = {op.name: op.value for op in op.Opcode}
        self.registers_dict = {'r'+str(i): i for i in range(32)}

    def encode(self, input_file_name='isa-encoder-input', output_file_name='isa-encoder-output', print_instructions=False):
        """
            Takes assembly file name (input_file_name), output file name (output_file_name) and creates the file with bytecode representation. 
        """

        tokens=[]

        text = ""
        # read the input file
        with open(input_file_name, "r") as read_file:
            text = read_file.read()

        # instantiate lexer and tokens
        lexer = AssemblyLexer()
        tokens = lexer.tokenize(text)

        self.labels = {}
        
        # write into the file
        with open(output_file_name, "wb") as write_file:

            # find labels
            i=0
            byte_index = 0
            # find labels' byte indexes
            while tokens[i].token_type != 'EOF':
                if tokens[i].token_type == 'OPCODE':
                    byte_index += 4

                elif tokens[i].token_type == 'LABEL':
                    self.labels[tokens[i].value] = byte_index
                
                i += 1

            # iterate over opcodes
            i=0
            while tokens[i].token_type != 'EOF':

                opcode  =0b0000_0000
                arg1    =0b0000_0000
                arg2    =0b0000_0000
                arg3    =0b0000_0000

                data    =bytes()

                

                # skip labels
                if tokens[i].token_type == 'LABEL':
                    i += 1
                    continue

                # opcode found
                elif tokens[i].token_type == 'OPCODE':
                    # opcode byte representation
                    opcode = self.opcodes_dict[tokens[i].value]

                    # DSS (8,8,8,8), DSI (8,8,8,8), DS (8,8,16), DI (8,8,16), I (8,24)
                    opcode_type = self._find_opcode_type(opcode)

                    if opcode_type == 'DSS':
                        # check if all arguments are present
                        if i+3 >= len(tokens):
                            raise SyntaxError(f"incomplete instruction with opcode {opcode} at line {tokens[i].line}")
                        
                        # convert names into register bytecode. Make sure they're 8 bit
                        arg1 = self.registers_dict[tokens[i+1].value]   & 0xFF
                        arg2 = self.registers_dict[tokens[i+2].value]   & 0xFF
                        arg3 = self.registers_dict[tokens[i+3].value]   & 0xFF

                        # make a single 32 bit instruction
                        data = struct.pack(">I", (opcode << 24) | (arg1 << 16) | (arg2 << 8) | arg3)

                        # skip opcode and arguments
                        i+=4

                    # the same logic applies here
                    elif opcode_type == 'DSI':
                        if i+3 >= len(tokens):
                            raise SyntaxError(f"incomplete instruction with opcode {opcode} at line {tokens[i].line}")
                        
                        arg1 = self.registers_dict[tokens[i+1].value]   & 0xFF
                        arg2 = self.registers_dict[tokens[i+2].value]   & 0xFF
                        arg3 = self._label_or_numeric(tokens[i+3], bits=8, called_from='DSI')      & 0xFF
                        data = struct.pack(">I", (opcode << 24) | (arg1 << 16) | (arg2 << 8) | arg3)

                        i+=4

                    # notice : arg2 for DS and DI, also arg1 for I, must be masked correctly and not shifted in order to make a correct instruction
                    elif opcode_type == 'DS':
                        if i+2 >= len(tokens):
                            raise SyntaxError(f"incomplete instruction with opcode {opcode} at line {tokens[i].line}")
                        
                        arg1 = self.registers_dict[tokens[i+1].value]   & 0xFF
                        arg2 = self.registers_dict[tokens[i+2].value]   & 0xFF

                        data = struct.pack(">I", (opcode << 24) | (arg1 << 16) | (arg2))

                        i+=3

                    elif opcode_type == 'DI':
                        if i+2 >= len(tokens):
                            raise SyntaxError(f"incomplete instruction with opcode {opcode} at line {tokens[i].line}")
                        
                        arg1 = self.registers_dict[tokens[i+1].value]   & 0xFF
                        arg2 = self._label_or_numeric(tokens[i+2], 16, called_from='DI')      & 0xFF_FF
                        data = struct.pack(">I", (opcode << 24) | (arg1 << 16) | (arg2))

                        i+=3

                    elif opcode_type == 'I':
                        if i+1 >= len(tokens):
                            raise SyntaxError(f"incomplete instruction with opcode {opcode} at line {tokens[i].line}")
                        
                        # 24 bit number
                        arg1 = self._label_or_numeric(tokens[i+1], 24, called_from='I')      & 0xFF_FF_FF
                        data = struct.pack(">I", (opcode << 24) | arg1)

                        i+=2

                    write_file.write(data)

                else:
                    raise SyntaxError(f"unknown token {tokens[i]}")
                
                if print_instructions:
                    print(opcode, arg1 , arg2, arg3)

                
    def decode(self, input_file_name='isa-encoder-output', output_file_name='isa-decoder-output', print_machine_code=False, lower_case=False):
        """
            ** notice that the input_file_name must be the output file of an encoder, i.e. contain byte code
            
            Takes bytecode file name (input_file_name), decoder output file name (output_file_name) and creates the file with assembly representation.  
            print_machine_code - whether to print the machine code during decoding process.
            lower_case         - whether to write assembly instructions in lower or upper case. If true, writes in lower case.

            Note that labels don't get decoded.

        """
        text = ""

        # open the file for byte reading
        with open(input_file_name, "rb") as file:
            byte_index=0

            while chunk := file.read(4): # read 4 bytes of memory in a single iteration
                byte_index+=1

                word = int.from_bytes(chunk, byteorder="big")
                
                # Instruction masking. Opcode is supposed to be the first byte, arg1 second byte, arg2 third and arg4 the forth.
                # After masking they are shifted to get the real bytecode representation
                opcode = (word     & 0xFF_00_00_00) >> 24
                arg1 =   (word     & 0x00_FF_00_00) >> 16
                arg2 =   (word     & 0x00_00_FF_00) >> 8
                arg3 =   (word     & 0x00_00_00_FF)

                if print_machine_code:
                    print(bin(word))

                # find type and opcode
                typ = self._find_opcode_type(opcode)
                opcode_reversed = self._opcode_reverse(opcode, byte_index)

                if lower_case:
                    opcode_reversed.lower()

                # depending on the type, decode the instruction and add to the text. Notice the default case is upper-case.
                if typ == 'DSS':
                    reg1_reverse = self._register_reverse(arg1, byte_index)
                    reg2_reverse = self._register_reverse(arg2, byte_index)
                    reg3_reverse = self._register_reverse(arg3, byte_index)

                    text += f"{opcode_reversed} {reg1_reverse}, {reg2_reverse}, {reg3_reverse}\n"
                elif typ == 'DSI':
                    reg1_reverse = self._register_reverse(arg1, byte_index)
                    reg2_reverse = self._register_reverse(arg2, byte_index)
                    arg3_full = word & 0x00_00_00_FF 

                    text += f"{opcode_reversed} {reg1_reverse}, {reg2_reverse}, {arg3_full}\n"
                elif typ == 'DS':
                    reg1_reverse = self._register_reverse(arg1, byte_index)

                    arg2_full = word & 0x00_00_FF_FF 

                    reg2_reverse = self._register_reverse(arg2_full, byte_index)

                    text += f"{opcode_reversed} {reg1_reverse}, {reg2_reverse}\n"
                elif typ == 'DI':
                    reg1_reverse = self._register_reverse(arg1, byte_index)
                    arg2_full = word & 0x00_00_FF_FF 

                    text += f"{opcode_reversed} {reg1_reverse}, {arg2_full}\n"
                elif typ == 'I':
                    reg1_reverse = self._register_reverse(arg1, byte_index)
                    arg1_full = word & 0x00_FF_FF_FF 

                    text += f"{opcode_reversed} {arg1_full}\n"
    
        # open the file to write the decoded instructions
        with open(output_file_name, "w") as file:
            file.write(text)

    #
    # UTILITY FUNCTIONS
    #
    def _opcode_reverse(self,number:int, error_occurance_place):
        for name, val in self.opcodes_dict.items():
            if val == number:
                return name
        
        raise SyntaxError(f"Unknown opcode byte representation {bin(number)} at {error_occurance_place}")
    
    def _register_reverse(self,number:int, error_occurance_place):
        for name, val in self.registers_dict.items():
            if val == number:
                return name
    
        raise SyntaxError(f"Unknown register byte representation {bin(number)} at {error_occurance_place}")

    def _find_opcode_type(self,opcode: int) -> str:
        if opcode & 0b1000_0000 == 0b1000_0000: # whether the opcode has the intermediate bit
            if opcode == self.opcodes_dict['JAL'] or opcode == self.opcodes_dict['LUI'] or opcode == self.opcodes_dict['LLI']:
                return 'DI'
            elif opcode == self.opcodes_dict['J']:
                return 'I'
            else:
                return 'DSI'
        else:
            if opcode == self.opcodes_dict['SEQZ']:
                return 'DS'
            else:
                return 'DSS'
    
    def _label_or_numeric(self, token, bits, called_from):
        if token.token_type == 'IDENTIFIER':
            if token.value in self.labels:
                return self.labels[token.value]
            else:
                raise RuntimeError(f"no known label {token}")

        elif token.token_type == 'HEX':
            return int(token.value, 16)
        elif token.token_type == 'NUMERIC':
            return int(token.value, 10)
        elif token.token_type == 'SIGNED':
            value = (1 << bits) + int(token.value)
            return value & ((1 << bits) - 1)
        else:
            raise SyntaxError(f"Compilation error from {called_from}: unknown label or numeric token {token}")


isa_compiler = ISA_compiler()

isa_compiler.encode('test_input.asm', 'output')
isa_compiler.decode('output', 'decoded')