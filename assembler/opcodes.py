# Opcodes file. Created on 21/6.
# Intent: Store all opcodes byte representations in a convenient way. Also contains explanations of the low-level design of ISA.
#           For high-level explanation visit explan_assembly.md

from enum import IntEnum

# first 3 bits are always free. In a sense, you can have at least 8 different opcodes for each type.

# EXPLANATION: ______________________________________________________________________
# first of all, note we use the big endian notation for simplified arithmetics (mul vs mulh for example)
#
# OK. So, Each CPU instruction will be fixed 32 bit length. Opcode will always be the first 8 bits.
# There are 5 possible instruction types: DSS, DSI, DS, DI, I. (D - destination, S - source, I - immediate)
# Each type except for I uses the second 8 bits as the destination, either a register or ram address.
#
# DSS - uses two registers and stores the operation on them into the destination
# 
# DSI - uses a single register (3rd byte) and an immediate value (4byte, thus 0-255) and stores into destination.
#       Note that some DSI instructions use the immediate as signed (2's complement) or unsigned. As the CPU stores them in binary
#           it's the work of the compiler to treat them as signed (e.g. addi) or unsigned (e.g. beq).
#       Labels are also stored as numbers, so the branching instruction use the immediate as the label address, 
#           but in theory they can use any number
# 
# DS - does operation on source register and stores it in D (e.g seqz)
#
# DI - does operation on immediate value and stores it in D (e.g. jal, lui and lli)
#
# I - right now it's only the jump instruction (j label or address)

# _______________________________________________

# These are the masks, in order to simplify making opcodes here.

# the last bit tells if the the 'last' byte (DSS vs DSI and DS vs DI) is immediate or not. 
IMMEDIATE_BIT                       = 0b1_00_0_0_000

# Notice the way we divide the masks. 

# Last bit - immediate
# 2nd and 3rd last - the 'type' of operation, not in DSS vs DSI sense, but whether it's arithmetic, logical, loading/storing or branching. 
# 5th and 6th last - to distinguish the 'subclass' of operations in the last 2nd+3rd bit class. For example, shift vs set both go into logical class (for CPU decoder convenience), but differ in the 5th+6th bit.
# first 3 bits - the actual opcode (add vs mul). They go sequentially.

# overall this means we have: 
# 1bit, immediate/not immediate
# 2bits, 4 possible operation types (arithmetic/logic/load_store/branching)
# 2bits, 4 possible subclasses (logic -> shifting/setting, load_store -> load/store, branching -> compare/jump etc). There're still unused subclasses
# 3bits, 8 possible operations for each subclass + class.

# Again, this design is for future cpu decoding convinience (e.g. MUXing second alu argument if immediate bit is on) and it is not going to change. 
# In future SIMD might be added on top, but already made opcodes will remain the same.

# arithmetic mask is the default. NOP uses this mask because it's the reserved 0x00 opcode, so that the memory doesn't read the zero bytes 'empty' space.
#                                       arithm
#                                         ||
ARITHMETIC_BIT                      = 0b0_00_0_0_000



#                                        logic
#                                         || |
LOGIC_BIT                           = 0b0_01_0_0_000

#                                           shift
#                                            | |
LOGIC_SHIFT_BIT                     = 0b0_01_1_0_000

#                                            set
#                                            | |
LOGIC_SET_BIT                       = 0b0_01_1_1_000



#                                       load_store
#                                         ||
LOADSTORE_BIT                       = 0b0_10_0_0_000
#                                           store
#                                            |
LOADSTORE_STORE_BIT                 = 0b0_10_0_0_000
#                                           load
#                                            |
LOADSTORE_LOAD_BIT                  = 0b0_10_1_0_000



#                                        branching
#                                         ||
BRANCHING_BIT                       = 0b0_11_0_0_000
#                                           jump (e.g jal, jalr, j)
#                                            |
JUMPING_BIT                         = 0b0_11_1_0_000


class Opcode(IntEnum):
    NOP   = 0b0000_0000 # reserved
    #### arithmetics, 5 used, 11 available
    ADD   = 0b0_000_0001|ARITHMETIC_BIT                                             #DSS
    MUL   = 0b0_000_0010|ARITHMETIC_BIT                                             #DSS
    MULH  = 0b0_000_0011|ARITHMETIC_BIT # multiply and store at higher (16) bits    #DSS
    DIV   = 0b0_000_0100|ARITHMETIC_BIT                                             #DSS
    REM   = 0b0_000_0101|ARITHMETIC_BIT                                             #DSS

    #shifting, 3 used, 13 available
    SLL   = 0b0_0000_000|LOGIC_SHIFT_BIT # shift left                               #DSS
    SRL   = 0b0_0000_001|LOGIC_SHIFT_BIT # shift right                              #DSS
    SRA   = 0b0_0000_010|LOGIC_SHIFT_BIT # shift right arithmetic                   #DSS
    # setters, 3 used, 13 available
    SLT   = 0b0_0000_000|LOGIC_SET_BIT # set less than                              #DSS
    SLTS  = 0b0_0000_001|LOGIC_SET_BIT # set less than signed                       #DSS
    SEQZ  = 0b0_0000_010|LOGIC_SET_BIT # set whether (source == 0).                 #DS  !

    # logic, 4 used, 12 available
    AND   = 0b0_000_0000|LOGIC_BIT                                                  #DSS
    OR    = 0b0_000_0001|LOGIC_BIT                                                  #DSS
    NOT   = 0b0_000_0010|LOGIC_BIT                                                  #DSS
    XOR   = 0b0_000_0011|LOGIC_BIT                                                  #DSS

    # immediate counterparts
    #arithmetics
    ADDI  = ADD   | IMMEDIATE_BIT                                                  #DSI
    #logic
    ANDI  = AND   | IMMEDIATE_BIT                                                  #DSI
    ORI   = OR    | IMMEDIATE_BIT                                                  #DSI
    XORI  = XOR   | IMMEDIATE_BIT                                                  #DSI
    #shifting & setting
    SLLI  = SLL   | IMMEDIATE_BIT                                                  #DSI
    SRLI  = SRL   | IMMEDIATE_BIT                                                  #DSI
    SRAI  = SRA   | IMMEDIATE_BIT                                                  #DSI
    SLTI  = SLT   | IMMEDIATE_BIT                                                  #DSI
    SLTSI = SLTS  | IMMEDIATE_BIT                                                  #DSI

    # load, 4 used, 12 a
    LB    = 0b0000_0000 | LOADSTORE_LOAD_BIT | IMMEDIATE_BIT #DSI loads a byte from ram with immediate offset + the source register into destination register
    LH    = 0b0000_0001 | LOADSTORE_LOAD_BIT | IMMEDIATE_BIT #DSI
    LW    = 0b0000_0010 | LOADSTORE_LOAD_BIT | IMMEDIATE_BIT #DSI

    LUI   = 0b0000_0011 | LOADSTORE_LOAD_BIT | IMMEDIATE_BIT # load upper immediate (i.e. store in register's last  16 bits) #DI  !
    LLI   = 0b0000_0100 | LOADSTORE_LOAD_BIT | IMMEDIATE_BIT # load lower immediate (i.e. store in register's first 16 bits) #DI  !
    
    # store, 3 used, 13 available#
    # use destination register with the immediate offset, source register as the value to store.
    SB    = 0b0000_0000 | LOADSTORE_STORE_BIT | IMMEDIATE_BIT  # store the first byte of the source into ram                #DSI
    SH    = 0b0000_0001 | LOADSTORE_STORE_BIT | IMMEDIATE_BIT  # store half-word (16-bits)                                  #DSI
    SW    = 0b0000_0010 | LOADSTORE_STORE_BIT | IMMEDIATE_BIT  # store word                                                 #DSI

    # branching, 7 used, 1 available
    BEQ   = 0B00000_000 | BRANCHING_BIT | IMMEDIATE_BIT                                                 #DSI
    BNEQ  = 0B00000_001 | BRANCHING_BIT | IMMEDIATE_BIT                                                 #DSI
    BLT   = 0B00000_010 | BRANCHING_BIT | IMMEDIATE_BIT                                                 #DSI
    BLE   = 0B00000_011 | BRANCHING_BIT | IMMEDIATE_BIT                                                 #DSI
    BLTS  = 0B00000_100 | BRANCHING_BIT | IMMEDIATE_BIT                                                 #DSI
    BLTES  = 0B00000_101 | BRANCHING_BIT | IMMEDIATE_BIT                                                #DSI

    # branching, 3 used, 13 available
    JALR  = 0B00000_000 | JUMPING_BIT | IMMEDIATE_BIT #DSI type. Jumps to the address at source + immediate offset. Saves the return address in destination register.
    
    JAL   = 0B00000_001 | JUMPING_BIT | IMMEDIATE_BIT # DI type! Jumps to the immediate value and saves the return address in the destination register.

    J     = 0B00000_010 | JUMPING_BIT | IMMEDIATE_BIT # I type!  Jumps to the immediate value (24 bits)
