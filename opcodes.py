from enum import IntEnum, auto

IMMEDIATE_BIT                       = 0b1_00_0_0_000

ARITHMETIC_BIT                      = 0b0_00_0_0_000
LOGIC_BIT                           = 0b0_01_0_0_000
LOGIC_SHIFT_BIT                     = 0b0_01_1_0_000
LOGIC_SET_BIT                       = 0b0_01_1_1_000
LOADSTORE_BIT                       = 0b0_10_0_0_000
LOADSTORE_STORE_BIT                 = 0b0_10_0_0_000
LOADSTORE_LOAD_BIT                  = 0b0_10_1_0_000
BRANCHING_BIT                       = 0b0_11_0_0_000
JUMPING_BIT                         = 0b0_11_1_0_000

class Opcode(IntEnum):
    # DSS
    NOP   = 0b0000_0000
    #### arithmetics, 5 used, 11 available
    ADD   = 0b0_000_0001|ARITHMETIC_BIT
    MUL   = 0b0_000_0010|ARITHMETIC_BIT
    MULH  = 0b0_000_0011|ARITHMETIC_BIT
    DIV   = 0b0_000_0100|ARITHMETIC_BIT
    REM   = 0b0_000_0101|ARITHMETIC_BIT

    #shifting, 3 used, 13 available
    SLL   = 0b0_0000_000|LOGIC_SHIFT_BIT # shift left
    SRL   = 0b0_0000_001|LOGIC_SHIFT_BIT # shift right
    SRA   = 0b0_0000_010|LOGIC_SHIFT_BIT # shift right arithmetic
    # setters, 3 used, 13 available
    SLT   = 0b0_0000_000|LOGIC_SET_BIT # set less than
    SLTS  = 0b0_0000_001|LOGIC_SET_BIT # set less than signed
    SEQZ  = 0b0_0000_010|LOGIC_SET_BIT

    # logic, 4 used, 12 available
    AND   = 0b0_000_0000|LOGIC_BIT
    OR    = 0b0_000_0001|LOGIC_BIT
    NOT   = 0b0_000_0010|LOGIC_BIT
    XOR   = 0b0_000_0011|LOGIC_BIT

    # immediate counterparts
    #arithmetics
    ADDI  = ADD   | IMMEDIATE_BIT
    #logic
    ANDI  = AND   | IMMEDIATE_BIT
    ORI   = OR    | IMMEDIATE_BIT
    XORI  = XOR   | IMMEDIATE_BIT
    #shifting & setting
    SLLI  = SLL   | IMMEDIATE_BIT
    SRLI  = SRL   | IMMEDIATE_BIT
    SRAI  = SRA   | IMMEDIATE_BIT
    SLTI  = SLT   | IMMEDIATE_BIT
    SLTSI = SLTS  | IMMEDIATE_BIT

    # load, 4 used, 12 a
    LB    = 0b0000_0000 | LOADSTORE_LOAD_BIT | IMMEDIATE_BIT 
    LH    = 0b0000_0001 | LOADSTORE_LOAD_BIT | IMMEDIATE_BIT 
    LW    = 0b0000_0010 | LOADSTORE_LOAD_BIT | IMMEDIATE_BIT 
    LUI   = 0b0000_0011 | LOADSTORE_LOAD_BIT | IMMEDIATE_BIT 
    
    # store, 3 used, 13 available
    SB    = 0b0000_0000 | LOADSTORE_STORE_BIT | IMMEDIATE_BIT 
    SH    = 0b0000_0001 | LOADSTORE_STORE_BIT | IMMEDIATE_BIT 
    SW    = 0b0000_0010 | LOADSTORE_STORE_BIT | IMMEDIATE_BIT 

    # branching, 7 used, 1 available
    BEQ   = 0B00000_000 | BRANCHING_BIT | IMMEDIATE_BIT
    BNEQ  = 0B00000_001 | BRANCHING_BIT | IMMEDIATE_BIT
    BLT   = 0B00000_010 | BRANCHING_BIT | IMMEDIATE_BIT
    BLE   = 0B00000_011 | BRANCHING_BIT | IMMEDIATE_BIT
    BLTS  = 0B00000_100 | BRANCHING_BIT | IMMEDIATE_BIT
    BTES  = 0B00000_101 | BRANCHING_BIT | IMMEDIATE_BIT

    # branching, 3 used, 13 available
    JALR  = 0B00000_000 | JUMPING_BIT | IMMEDIATE_BIT
    JAL   = 0B00000_001 | JUMPING_BIT | IMMEDIATE_BIT
    J     = 0B00000_010 | JUMPING_BIT | IMMEDIATE_BIT
