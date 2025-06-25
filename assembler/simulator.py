#########################################################
#   ISA bytecode simulator. Created on 24/6/25
#   Intent: Made for testing. Simulates a simple CPU with 256 byte ram and 32 registers.

#           Because python modules are a hell to work with, I just copied the utility functions from ISA_Compiler.py file.
#           Ideally they should be separated, but they are not supposed to be modified anyway.

# TODO: write a better test. Compare the result with desired output.

import opcodes as op
import struct

from assembly_lexer import AssemblyLexer

# TODO : write tests. Check lexer also.

class AssemblySimulator:
    def __init__(self):
        self.opcodes_dict = {op.name: op.value for op in op.Opcode}
        self.registers_dict = {'r'+str(i): i for i in range(32)}

        self.registers_file = {'r'+str(i): 0 for i in range(32)}
        self.RAM = {i : 0 for i in range(256)} # 256 byte ram

    def simulate(self, input_file_name='isa-encoder-output', log_registers = False, log_ram=False,
                 print_instructions = False,
                 early_stopping = False, max_iterations=2**32):
        """
            * notice: file must be in bytecode instruction form, not handwritten assembly file.
            Simulates the machine code file assembly. Uses 32 registers and a 256 byte ram.

            log_registers - if True, prints the registers' values at every iteration.
            log_ram - if True, prints the ram values at every iteration.
            early_stopping - if True, iterates only till max_iterations argument. Each iteration is a single 32 bit instruction.
        """

        # read file data
        data = ""
        with open(input_file_name, "rb") as f:
            data = f.read()

        i = 0
        while (i < len(data)):
            if early_stopping and i >= max_iterations*4:
                break

            chunk = data[i:i+4]

            word = int.from_bytes(chunk, byteorder="big")
            
            # Instruction masking. Opcode is supposed to be the first byte, arg1 second byte, arg2 third and arg4 the forth.
            # After masking they are shifted to get the real bytecode representation
            opcode = (word     & 0xFF_00_00_00) >> 24
            arg1 =   (word     & 0x00_FF_00_00) >> 16
            arg2 =   (word     & 0x00_00_FF_00) >> 8
            arg3 =   (word     & 0x00_00_00_FF)


            # find type and opcode
            typ = self._find_opcode_type(opcode)
            opcode_reversed = self._opcode_reverse(opcode, i)
            if print_instructions:
                print('\n',opcode_reversed, arg1, arg2, arg3, " : ", i)

            # depending on the type, decode the instruction and add to the text. Notice the default case is upper-case.
            if typ == 'DSS':
                reg1_reverse = self._register_reverse(arg1, i)
                reg2_reverse = self._register_reverse(arg2, i)
                reg3_reverse = self._register_reverse(arg3, i)

                self.simulate_dss(opcode_reversed, reg1_reverse, reg2_reverse, reg3_reverse)
            elif typ == 'DSI':
                reg1_reverse = self._register_reverse(arg1, i)
                reg2_reverse = self._register_reverse(arg2, i)

                # change the index in case of branching or jumping
                i = self.simulate_dsi(opcode_reversed, reg1_reverse, reg2_reverse, arg3, i)

            elif typ == 'DS':
                reg1_reverse = self._register_reverse(arg1, i)
                arg2_full = word & 0x00_00_FF_FF 

                reg2_reverse = self._register_reverse(arg2_full, i)

                self.simulate_ds(opcode_reversed, reg1_reverse, reg2_reverse)
                
            elif typ == 'DI':
                reg1_reverse = self._register_reverse(arg1, i)
                arg2_full = word & 0x00_00_FF_FF 

                i = self.simulate_di(opcode_reversed, reg1_reverse, arg2_full, i)

            elif typ == 'I':
                reg1_reverse = self._register_reverse(arg1, i)
                arg1_full = word & 0x00_FF_FF_FF 

                i = self.simulate_i(opcode_reversed, arg1_full)

            if log_registers:
                for r in self.registers_file:
                    print(self.registers_file[r], end = ',')
                print()

            if log_ram:
                print("RAM ___________")
                for addr in self.RAM:
                    print(self.RAM[addr], end = ',')
                print()

            i += 4

    #
    # OPCODE TYPE SIMULATIONS
    #
    def simulate_dss(self, opcode, reg1, reg2, reg3):
        # ARITHMETIC:   add, mul, mulh, div, rem
        # LOGIC:        and, or, xor, not
        # SHIFT:        sll, srl, sra
        # COMPARE:      slt, slts, seqz
        reg2_val = self.registers_file[reg2]
        reg3_val = self.registers_file[reg3]

        #ARITHMETIC

        if opcode == 'ADD':
            self._write_register(reg1, reg2_val + reg3_val)
        elif opcode == 'MUL':
            self._write_register(reg1, (reg2_val * reg3_val) & 0x0000_FFFF)
        elif opcode == 'MULH':
            result = reg2_val * reg3_val
            self._write_register(reg1, (result << 16) & 0xFFFF_0000)
        elif opcode == 'DIV':
            try:
                self._write_register(reg1, int(reg2_val / reg3_val))
            except:
                raise ZeroDivisionError(f"Divison by zero at div instruction {opcode} {reg1}, {reg2}, {reg3}. Values of registers: {self.registers_file[reg1]}, {reg2_val}, {reg3_val}")
        elif opcode == 'REM':
            self._write_register(reg1, reg2_val % reg3_val)
        
        #LOGIC
        elif opcode == 'AND':
            self._write_register(reg1, reg2_val & reg3_val)
        elif opcode == 'OR':
            self._write_register(reg1, reg2_val | reg3_val)
        elif opcode == 'XOR':
            self._write_register(reg1, reg2_val ^ reg3_val)
        elif opcode == 'NOT':
            self._write_register(reg1, ~reg2_val)
            
        #SHIFTING
        elif opcode == 'SLL':
            self._write_register(reg1, reg2_val << reg3_val)
        elif opcode == 'SRL':
            self._write_register(reg1, reg2_val >> reg3_val)
        elif opcode == 'SRA':
            self.registers_file[reg1] = reg2_val >> reg3_val if reg2_val >= 0 else -((-reg2_val) >> reg3_val)


        #COMPARE
        elif opcode == 'SLT':
            self._write_register(reg1, int(abs(reg2_val) < abs(reg3_val)))
        elif opcode == 'SLTS':
            self._write_register(reg1, int(reg2_val < reg3_val))

        elif opcode == 'NOP':
            pass
    
        else:
            raise RuntimeError(f"Unknown opcode {repr(opcode)} during dss simulation")


    def simulate_dsi(self, opcode, reg1, reg2, imm, cursor_byte):

        reg1_val = self.registers_file[reg1]
        reg2_val = self.registers_file[reg2]

        # addi, andi, ori, xori, slli, srli, srai, slti, sltsi
        if opcode == 'ADDI':
            imm = self._sign_extend(imm, 8, 32)

            self._write_register(reg1, reg2_val + imm)
        elif opcode == 'ANDI':
            self._write_register(reg1, reg2_val & imm)
        elif opcode == 'ORI':
            self._write_register(reg1, reg2_val | imm)
        elif opcode == 'XORI':
            self._write_register(reg1, reg2_val ^ imm)

        #SHIFTING
        elif opcode == 'SLLI':
            self._write_register(reg1, reg2_val << imm)
        elif opcode == 'SRLI':
            self._write_register(reg1, reg2_val >> imm)
        elif opcode == 'SRAI':
            self.registers_file[reg1] = reg2_val >> imm if reg2_val >= 0 else -((-reg2_val) >> imm)

        #COMPARE
        elif opcode == 'SLTI':
            self._write_register(reg1, int(abs(reg2_val) < abs(imm)))
        elif opcode == 'SLTSI':
            imm = self._sign_extend(imm, 8, 32)
            self._write_register(reg1, int(reg2_val < imm))

        #LOADING
        elif opcode == 'LB':

            self._write_register(reg1, self.RAM[reg2_val + imm] & 0xFF)
        elif opcode == 'LH':
            imm = self._sign_extend(imm, 8, 16)

            self._write_register(reg1, self.RAM[reg2_val + imm] & 0xFFFF)
        elif opcode == 'LW':
            imm = self._sign_extend(imm, 8, 32)

            self._write_register(reg1, self.RAM[reg2_val + imm])

    
        #SAVING
        elif opcode == 'SB':

            self.RAM[reg1_val + imm] = reg2_val & 0xFF
        elif opcode == 'SH':
            imm = self._sign_extend(imm, 8, 16)

            self.RAM[reg1_val + imm] = reg2_val & 0xFFFF
        elif opcode == 'SW':
            imm = self._sign_extend(imm, 8, 32)

            self.RAM[reg1_val + imm] = reg2_val

        # branching beq, bneq, blt, ble, blts, bltes

        # note that branches never sign extend. The immediate is supposed to be a label.
        elif opcode == 'BEQ':
            if reg1_val == reg2_val:
                return imm - 4
        elif opcode == 'BNEQ':

            if reg1_val != reg2_val:
                return imm - 4
        elif opcode == 'BLT':
            if abs(reg1_val) < abs(reg2_val):
                return imm - 4
        elif opcode == 'BLE':
            if abs(reg1_val) <= abs(reg2_val):
                return imm - 4
        elif opcode == 'BLTS':
            # we don't sign extend the immediate value cuz we assume label is only positive

            if reg1_val < reg2_val:
                return imm - 4
        elif opcode == 'BLTES':

            if reg1_val < reg2_val:
                return imm - 4
        
        # jump
        elif opcode == 'JALR':
            self._write_register(reg1, cursor_byte)
            return reg2_val + imm
        
        else:
            raise RuntimeError(f"Unknown opcode {repr(opcode)} during dsi simulation")

        return cursor_byte

    def simulate_ds(self, opcode, reg1, reg2):
        if opcode == 'SEQZ':
            val = int(self.registers_file[reg2] == 0)
            self._write_register(reg1, val)
            
        else:
            raise RuntimeError(f"Unknown opcode {repr(opcode)} during ds simulation")     

    def simulate_di(self, opcode, reg, imm, cursor_byte):
        
        # opcode 8, reg 8, imm 16
        
        # these 3 operations are unsigned
        if opcode == 'JAL':
            self._write_register(reg, cursor_byte)
            return imm - 4
        
        elif opcode == 'LUI':
            self._write_register(reg, (self.registers_file[reg] & 0x0000_FFFF) | (imm << 16))
        elif opcode == 'LLI':
            self._write_register(reg, (self.registers_file[reg] & 0xFFFF_0000) | imm)

        else:
            raise RuntimeError(f"Unknown opcode {repr(opcode)} during di simulation")     
        
        return cursor_byte 
    
    def simulate_i(self, opcode, imm):
        # notice we don't treat imm as signed
        # opcode 8, reg 8, imm 16
        if opcode == 'J':
            return imm - 4
        else:
            raise RuntimeError(f"Unknown opcode {repr(opcode)} during i simulation" )     

    def _write_register(self, reg, val):
        """ writes into the register, where reg is the name ('r0' through 'r31'). Keeps r0 constantly 0."""
        if reg == 'r0':
            return 0
        self.registers_file[reg] = val & 0xFF_FF_FF_FF

    def _sign_extend(self, value, input_bits, output_bits):
        """
            if the number is negative in input_bits size, it extends the number into output_bits size, while keeping the value.
            i.e. it keeps the absolute part unchanged and moves the last bit into new size's last bit.
        """
        mask = (1 << output_bits) - 1
        sign_bit = 1 << (input_bits - 1)
        if value & sign_bit:  # If negative
            value |= (2**(output_bits)-1) - (2**(input_bits)-1)
            return value & mask
        else:
            return value 
    
    def _is_negative_twos_complement(self,x, n_bits):
        """ returns if x is negative in two's complement. I.e. if its last bit is on. """
        if x >= (1 << (n_bits - 1)):  # If x ≥ 2^(n_bits-1), it's negative
            return True
        return False

    #
    # UTILITY FUNCTIONS. Copied from isa_compiler.py
    # DO NOT MODIFY
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

TESTING = True

if TESTING:
    simulator = AssemblySimulator()
    simulator.simulate('output', log_registers=True, print_instructions=True, log_ram=True)