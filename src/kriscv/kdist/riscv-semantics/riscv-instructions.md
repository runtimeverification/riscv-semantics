# Instruction Syntax
In this file, we define the basic syntax for disassembled instructions.

We closely mirror the ASM syntax as output by the RISC-V GNU Toolchain's `objdump`. In particular,
- I-Type and S-Type instructions with 12-bit signed immediates (e.g., `addi` but not `slli`) take an immediate argument in the range `[-2048, 2047]`.
- Shift instructions take a shift amount argument in the range `[0, XLEN - 1]`.
- U-Type instruction take an immediate argument in the range `[0x0, 0xfffff]`, i.e., not representing the zeroed-out 12 least-significant bits.
- B-Type instructions take an immediate argument as an even integer in the range `[-4096, 4094]`, i.e., explicitly representing the zeroed-out least-significant bit.
- J-Type instructions take an immediate argument as an even integer in the range `[-1048576, 1048574]`, i.e., explicitly representing the zeroed-out least-significant bit.

A register `xi` is simply represented by the `Int` value `i`.
```k
module RISCV-INSTRUCTIONS
  imports INT

  syntax Register ::= Int

  syntax Instruction ::=
      RegRegImmInstr
    | RegImmInstr
    | RegRegRegInstr
    | RegImmRegInstr
    | FenceInstr
    | NullaryInstr
    | InvalidInstr

  syntax RegRegImmInstr ::= RegRegImmInstrName Register "," Register "," Int [symbol(RegRegImmInstr)]
  syntax RegRegImmInstrName ::=
      "ADDI"  [symbol(ADDI)]
    | "SLTI"  [symbol(SLTI)]
    | "SLTIU" [symbol(SLTIU)]
    | "ANDI"  [symbol(ANDI)]
    | "ORI"   [symbol(ORI)]
    | "XORI"  [symbol(XORI)]
    | "SLLI"  [symbol(SLLI)]
    | "SRLI"  [symbol(SRLI)]
    | "SRAI"  [symbol(SRAI)]
    | "BEQ"   [symbol(BEQ)]
    | "BNE"   [symbol(BNE)]
    | "BLT"   [symbol(BLT)]
    | "BLTU"  [symbol(BLTU)]
    | "BGE"   [symbol(BGE)]
    | "BGEU"  [symbol(BGEU)]

  syntax RegImmInstr ::= RegImmInstrName Register "," Int [symbol(RegImmInstr)]
  syntax RegImmInstrName ::=
      "LUI"   [symbol(LUI)]
    | "AUIPC" [symbol(AUIPC)]
    | "JAL"   [symbol(JAL)]

  syntax RegRegRegInstr ::= RegRegRegInstrName Register "," Register "," Register [symbol(RegRegRegInstr)]
  syntax RegRegRegInstrName ::=
      "ADD"  [symbol(ADD)]
    | "SUB"  [symbol(SUB)]
    | "SLT"  [symbol(SLT)]
    | "SLTU" [symbol(SLTU)]
    | "AND"  [symbol(AND)]
    | "OR"   [symbol(OR)]
    | "XOR"  [symbol(XOR)]
    | "SLL"  [symbol(SLL)]
    | "SRL"  [symbol(SRL)]
    | "SRA"  [symbol(SRA)]

  syntax RegImmRegInstr ::= RegImmRegInstrName Register "," Int "(" Register ")" [symbol(RegImmRegInstr)]
  syntax RegImmRegInstrName ::=
      "JALR" [symbol(JALR)]
    | "LW"   [symbol(LW)]
    | "LH"   [symbol(LH)]
    | "LHU"  [symbol(LHU)]
    | "LB"   [symbol(LB)]
    | "LBU"  [symbol(LBU)]
    | "SW"   [symbol(SW)]
    | "SH"   [symbol(SH)]
    | "SB"   [symbol(SB)]

  syntax FenceInstr ::= "FENCE" Int "," Int [symbol(FENCE)]

  syntax NullaryInstr ::= NullaryInstrName
  syntax NullaryInstrName ::=
      "FENCE.TSO" [symbol(FENCETSO)]
    | "ECALL"     [symbol(ECALL)]
    | "EBREAK"    [symbol(EBREAK)]

  syntax InvalidInstr ::= "INVALID_INSTR" [symbol(INVALID_INSTR)]
endmodule
```
