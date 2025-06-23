import opcodes as op
import struct

# TODO: 1) make a better workflow. Take as program arguments whether to decode or encode.
#       2) make error handling and messaging
#       3) add labels support

ENCODE=False
DECODE=True

opcodes_dict = {op.name: op.value for op in op.Opcode}

def opcode_reverse(number):
    for name, val in opcodes_dict.items():
        if val == number:
            return name
    return None


def find_opcode_type(opcode):
    if opcode & 0b1000_0000 == 0b1000_0000:
        if opcode == opcodes_dict['JAL'] or opcode == opcodes_dict['LUI']:
            return 'DI'
        elif opcode == opcodes_dict['J']:
            return 'I'
        else:
            return 'DSI'
    else:
        if opcode == opcodes_dict['SEQZ']:
            return 'DS'
        else:
            return 'DSS'

# registers r0,...,r31
registers_dict = {}
for i in range(32):
    registers_dict['r'+str(i)]=i

def register_reverse(number):
    for name, val in registers_dict.items():
        if val == number:
            return name
    return None

if ENCODE:
    lines=[]
    with open("input", "r") as file:
        text = file.read()
        # splitting text into lines
        lines = text.splitlines()
        while '' in lines:
            lines.remove('')
    
    with open("output", "wb") as file:
        
        # iterating over instructions
        for l in lines:
            split = l.split()
            opcode = split[0].upper()
            opcode_byte = opcodes_dict[split[0].upper()]
            opcode_type = find_opcode_type(opcode_byte)

            dest, src1, src2, imm, data = 0,0,0,0,bytes()

            if opcode_type == 'DSS':
                split[1] = split[1][:-1]
                split[2] = split[2][:-1]

                dest = registers_dict[split[1]]
                src1 = registers_dict[split[2]]
                src2 = registers_dict[split[3]]

                data = struct.pack(">I", (opcode_byte << 24) | (dest << 16) | (src1 << 8) | src2)

            elif opcode_type == 'DSI':
                split[1] = split[1][:-1]
                split[2] = split[2][:-1]

                dest = registers_dict[split[1]]
                src1 = registers_dict[split[2]]
                imm =  int(split[3])

                data = struct.pack(">I", (opcode_byte << 24) | (dest << 16) | (src1 << 8) | imm)

            elif opcode_type == 'DS':
                split[1] = split[1][:-1]
            
                dest = registers_dict[split[1]]
                src1 = registers_dict[split[2]]

                data = struct.pack(">I", (opcode_byte << 24) | (dest << 16) | (src1<<8))

            elif opcode_type == 'DI':
                split[1] = split[1][:-1]

                dest = registers_dict[split[1]]
                imm =  int(split[2])

                data = struct.pack(">I", (opcode_byte << 24) | (dest << 16) | (imm<<8))

            elif opcode_type == 'I':
                imm =  int(split[1])

                data = struct.pack(">I", (opcode_byte << 24) | (imm << 16))

            file.write(data)


PRINT_MACHINECODE = False
if DECODE:
    text = ""
    with open("output", "rb") as file:
        while chunk := file.read(4):
            word = int.from_bytes(chunk, byteorder="big")
            # print(f"{word:032b}")
            opcode = (word     & 0b11111111_00000000_00000000_00000000) >> 24
            arg1 =   (word     & 0b00000000_11111111_00000000_00000000) >> 16
            arg2 =   (word     & 0b00000000_00000000_11111111_00000000) >> 8
            arg3 =   (word     & 0b00000000_00000000_00000000_11111111)

            if PRINT_MACHINECODE:
                print(bin(word))

            typ = find_opcode_type(opcode)
            opcode_reversed = opcode_reverse(opcode)
            reg1_reverse = register_reverse(arg1)
            reg2_reverse = register_reverse(arg2)

            if typ == 'DSS':
                text += f"{opcode_reversed} {reg1_reverse}, {reg2_reverse}, {register_reverse(arg3)}\n"
            elif typ == 'DSI':
                text += f"{opcode_reversed} {reg1_reverse}, {reg2_reverse}, {arg3}\n"
            elif typ == 'DS':
                text += f"{opcode_reversed} {reg1_reverse}, {reg2_reverse}\n"
            elif typ == 'DI':
                text += f"{opcode_reversed} {reg1_reverse}, {arg2}\n"
            elif typ == 'I':
                text += f"{opcode_reversed} {arg1}\n"
    
    with open("decoded", "w") as file:
        file.write(text)