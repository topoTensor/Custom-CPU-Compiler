#########################################################
#   ISA encoder/decoder file. Created on 21/6/25
#   Intent: Created separately for the compiler project. 
#           The main purpose was to abstract the process of translating assembly into bytecode.
#           It also contains functionality for decoding the bytecode back into the assembly language.
#
#           Uses custom ISA, made by me for my custom CPU architecture.
#           For details look at the opcodes.py file, which contains details about opcodes' byte representations..

#         * For high-level details look at the 'explain_assembly' file


import opcodes as op
import struct

#       2) make error handling and messaging
#       3) add labels support

class ISA_compiler:
    def __init__(self):
        self.opcodes_dict = {op.name: op.value for op in op.Opcode}
        self.registers_dict = {'r'+str(i): i for i in range(32)}

    def encode(self, input_file_name='isa-encoder-input', output_file_name='isa-encoder-output'):
        """
            Takes assembly file name (input_file_name), output file name (output_file_name) and creates the file with bytecode representation. 
        """
        lines=[]

        # read the input file, split it by new lines, remove all '' from the list.
        with open(input_file_name, "r") as file:
            text = file.read()
            lines = text.splitlines()
            # while '' in lines: DON'T REMOVE THEM, USED AT LINE INDEXING FOR ERRORS
            #     lines.remove('')
        
        line_index = 0
        # write binary into the file
        with open(output_file_name, "wb") as file:
            
            # iterating over instructions
            for l in lines:
                line_index+=1
                # skip empty lines
                if l == '':
                    continue

                # splits the instruction (e.g. add a,b,c into ['add' 'a,' 'b,' 'c'], notice the commas)
                split = l.split() # split has dynamic size and depends on the instruction type (namely DSS - 4, DSI - 4, DS - 3, DI - 3, I - 2)
                opcode_byte = self.opcodes_dict[split[0].upper()] # opcode byte representation
                opcode_type = self._find_opcode_type(opcode_byte) # returns the instruction type given the bytecode

                dest, src1, src2, imm, data = 0,0,0,0,bytes() # pre-define bytecodes

                # as the syntax is of the form "opcode dest, src, src" for DSS, we should remove the commas for each argument

                if opcode_type == 'DSS': # opcode dest, src, src
                    split[1] = split[1][:-1] # remove comma from argument 1
                    split[2] = split[2][:-1] # remove comma from argument 2

                    dest = self.registers_dict[split[1]]
                    src1 = self.registers_dict[split[2]]
                    src2 = self.registers_dict[split[3]]

                    data = struct.pack(">I", (opcode_byte << 24) | (dest << 16) | (src1 << 8) | src2) # 32 bit bytecode instruction

                # the same logic follows all other instruction types
                elif opcode_type == 'DSI': # opcode dest, src, imm
                    split[1] = split[1][:-1]
                    split[2] = split[2][:-1]

                    dest = self.registers_dict[split[1]]
                    src1 = self.registers_dict[split[2]]
                    imm =  int(split[3])

                    data = struct.pack(">I", (opcode_byte << 24) | (dest << 16) | (src1 << 8) | imm)

                elif opcode_type == 'DS': # opcode dest, src
                    split[1] = split[1][:-1]
                
                    dest = self.registers_dict[split[1]]
                    src1 = self.registers_dict[split[2]]

                    data = struct.pack(">I", (opcode_byte << 24) | (dest << 16) | (src1<<8))

                elif opcode_type == 'DI': # opcode dest, imm
                    split[1] = split[1][:-1]

                    dest = self.registers_dict[split[1]]
                    imm  = int(split[2])

                    data = struct.pack(">I", (opcode_byte << 24) | (dest << 16) | (imm<<8))

                elif opcode_type == 'I': # opcode imm
                    imm  = int(split[1])

                    data = struct.pack(">I", (opcode_byte << 24) | (imm << 16))
                else:
                    raise RuntimeError(f"unknown instruction type {opcode_type} during isa-encoding at line {line_index} : {l}")

                # write the bytecode instruction in file
                file.write(data)

    def decode(self, input_file_name='isa-encoder-output', output_file_name='isa-decoder-output', print_machine_code=False, lower_case=False):
        """
            ** notice that the input_file_name must be the output file of an encoder, i.e. contain byte code
            
            Takes bytecode file name (input_file_name), decoder output file name (output_file_name) and creates the file with assembly representation.  
            print_machine_code - whether to print the machine code during decoding process.
            lower_case         - whether to write assembly instructions in lower or upper case. If true, writes in lower case.
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
                opcode = (word     & 0b11111111_00000000_00000000_00000000) >> 24
                arg1 =   (word     & 0b00000000_11111111_00000000_00000000) >> 16
                arg2 =   (word     & 0b00000000_00000000_11111111_00000000) >> 8
                arg3 =   (word     & 0b00000000_00000000_00000000_11111111)

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

                    text += f"{opcode_reversed} {reg1_reverse}, {reg2_reverse}, {self._register_reverse(arg3, byte_index)}\n"
                elif typ == 'DSI':
                    reg1_reverse = self._register_reverse(arg1, byte_index)
                    reg2_reverse = self._register_reverse(arg2, byte_index)

                    text += f"{opcode_reversed} {reg1_reverse}, {reg2_reverse}, {arg3}\n"
                elif typ == 'DS':
                    reg1_reverse = self._register_reverse(arg1, byte_index)
                    reg2_reverse = self._register_reverse(arg2, byte_index)

                    text += f"{opcode_reversed} {reg1_reverse}, {reg2_reverse}\n"
                elif typ == 'DI':
                    reg1_reverse = self._register_reverse(arg1, byte_index)

                    text += f"{opcode_reversed} {reg1_reverse}, {arg2}\n"
                elif typ == 'I':
                    reg1_reverse = self._register_reverse(arg1, byte_index)

                    text += f"{opcode_reversed} {arg1}\n"
    
        # open the file to write the decoded instructions
        with open(output_file_name, "w") as file:
            file.write(text)

    #
    # UTILITY FUNCTIONS
    #
    def _opcode_reverse(self,number, error_occurance_place):
        for name, val in self.opcodes_dict.items():
            if val == number:
                return name
        
        raise SyntaxError(f"Unknown opcode byte representation {bin(number)} at {error_occurance_place}")
    
    def _register_reverse(self,number, error_occurance_place):
        for name, val in self.registers_dict.items():
            if val == number:
                return name
    
        raise SyntaxError(f"Unknown register byte representation {bin(number)} at {error_occurance_place}")

    def _find_opcode_type(self,opcode) -> str:
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
            



isa_compiler = ISA_compiler()

isa_compiler.encode('input', 'output')
isa_compiler.decode('output', 'decoded')