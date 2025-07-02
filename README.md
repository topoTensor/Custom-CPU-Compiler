# Custom CPU Compiler

A lightweight experimental compiler written in Python for my custom-built Verilog CPU.  
This project is a **work in progress** and subject to major redesigns as the CPU and instruction set architecture (ISA) evolve.

The repository also contains a custom ISA assembler, disassembler and simulator.

## Project Goals

The first version of the language aims to support:

- Integer types  
- Arithmetic and bitwise operations  
- Control flow: `if`, `else if`, `else`, and `while`  
- Function definitions and calls  

Support for I/O, arrays, and strings is currently **not planned**, since implementing features like `print()` would require simulating an operating system or at least a virtual machine — which is beyond the current scope of this CPU.

## Implementation Checklist

### Assembler
- [x] Lexer
- [x] Encoder and Decoder
- [x] Parser
- [x] Custom ISA and bytecode
- [x] Tests
- [x] Simulator
- [x] Detailed explanation

### Compiler Components
- [x] Lexer
- [x] Parser
- [ ] Semantic analyzer (work in progress)
- [ ] Code generator (to custom ISA)
- [ ] Optimizer

### Future Extensions
- [ ] Support for arrays
- [ ] Support for strings
- [ ] Basic I/O functions
- [ ] Virtual machine simulation
- [ ] Standard library functions

## Example Syntax

```ruby
# Comments start with a hashtag.
a = 10;
b = 12;
c = a + b;  # Other operations: -, *, /, &, |, ^, ~, <<, >>

if (a < b) {
  # do something.
}; else if (a > b) {
  # branching
}; else {
  # do something else
};

i = 0;
while (i < 10) {
  i = i + 1;
};

function add(a, b) {
  return a + b;
};
