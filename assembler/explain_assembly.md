> **Note:** Though the CPU architecture dictates the limitations and possibilities of the instruction set, some ideas remain stable unless new features (such as SIMD or Atomic operations) are introduced. These core ideas are illustrated here. For low-level details, visit opcodes.py file.

# Note that labels end with ':' symbol. Nothing should follow the column after the label name. The next instruction must start with a new line.
# Comments start with ; and go through the end of the line.

```asm
A single instruction consists of 4 bytes: opcode, destination, source1, source2. Though this representation is fixed, depending on the opcodes the assembler might dissmiss the arguments (one or two sources).
```

```asm
Each source is a register (r0-r31). r0 is the constant zero register.
```

```asm
The assembly supports 5 types of opcodes. They are:
```

```asm
| Format | Fields                                   | Example             |
| ------ | ---------------------------------------- | ------------------- |
| DSS    | opcode, dest, src1, src2                 | `add r1, r2, r3`    |
| DSI    | opcode, dest, src, imm                   | `addi r1, r2, 0x10` |
| DI     | opcode, dest, imm (16-bit)               | `lui r1, 0x12`      |
| I      | opcode, imm (24-bit)                     | `j 0x123456`        |
```


### DSS - opcode destination, source1, source2.
#### ARITHMETICS

```asm
add     - adds two source registers, saves in destination register
mul     - multiplies two registers, saves first 32 bits of the result in the destination register
( note that multiplying two 32-bit values gives 64-bit value)
mulh    - multiplies two registers, saves last 32 bits of the result in the destination register
div     - integer division of two source registers
rem     - remainder of two registers after division
```

#### LOGIC

```asm
and, or, xor    - logical AND, OR, XOR operators
not             - logical not operator, ignores the second source register
```

#### SHIFTING

```asm
sll     - shifts left the first source register by second register's value, saves in destination
srl     - shifts right
sra     - arithmetic shift right
```


#### SETTERS

```asm
slt     - sets the destination register with the value (source1 < source2)
slts    - signed variation of slt instruction opcode
```

> **Note:** even though the first argument is still named destination, branching instructions use address stored as the immediate value.
### DSI - opcode destination, source, immediate value.

### Immediate counterparts of DSS type opcodes - addi, andi, ori, xori, slli, srli, srai, slti, sltsi

```asm
LOADING
```

```asm
lb - load a single byte from ram location of source register value + immediate offset into the destination register.
lh - loads half-word (16 bits) from ram by source+offset
lw - loads word (32 bits) from ram by source+offset
```

```asm
SAVING
```

```asm
sb - saves a single byte of source register into the address stored in destination register + offset
sh, sw - half word and word variants of sb
```

```asm
BRANCHING
```

```asm
beq     - branch if equal. Jumps to the immediate address if the destination register equals the source register.
bneq    - branch if not equal
blt     - branch if less than
ble     - branch if less than or equal
blts    - branch if less than           (signed variant)
bltes   - branch if less than or equal  (signed variant)
```

```asm
jalr    - jump and link register. Jumps to the address at source + immediate offset. Saves the return address in destination register.
```

### DS - opcode destination, source

```asm
seqz - set equal to zero. Sets the destination register the value of (source == 0)
```

### DI - opcode destination, immediate

```asm
jal - jump and link. Jumps to the immediate value and saves the return address in the destination register.
```

```asm
lui - loads the immediate value (which is 16 bits long) into the upper part of the destination register.
lli - loads the immediate value into the lower part of the destination register.
```

### I - opcode immediate

```asm
j - jumps to the immediate value (24-bit)
```

> **Note:** because 'addi r1, r0, imm' instruction supports only 8 bit immediate value, to load a single 32 bit value into the register, you need to use both lui and lli. e.g. To store 0x1234 into register r1, write 'lui r1, 0x12' and 'lli r1, 0x34'

```asm
COMPACT SUMMARY _____________________________________________________________________
```

```asm
ARITHMETIC:   add, mul, mulh, div, rem
LOGIC:        and, or, xor, not
SHIFT:        sll, srl, sra
COMPARE:      slt, slts, seqz
```
### IMMEDIATE:    addi, andi, ori, xori, slli, srli, srai, slti, sltsi
```asm
LOAD:         lb, lh, lw
STORE:        sb, sh, sw
BRANCH:       beq, bneq, blt, ble, blts, bltes
JUMP:         jal, jalr, j
LOAD IMM:     lui, lli
```