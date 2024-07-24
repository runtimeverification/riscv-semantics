# Disassembler
In this file, we implement the instruction disassembler, converting raw instruction bits to the syntax defined in [riscv-intructions.md](./riscv-instructions.md).
```k
requires "riscv-instructions.md"
requires "word.md"

module RISCV-DISASSEMBLE
  imports RISCV-INSTRUCTIONS
  imports INT
  imports STRING
  imports WORD
```
The input is given as an `Int` with the instruction stored in the 32 least-significant bits.
```k
  syntax Instruction ::= disassemble(Int) [symbol(disassemble), function, total, memo]
  rule disassemble(I:Int) => disassemble(decode(I))
```
Disassembly is then done in two phases:
- Separate out the component fields of the instruction based on its format (R, I, S, B, U, or J), returning an `InstructionFormat` value.
- Inspect the fields of the resulting `InstructionFormat` to produce the disassembled instruction.

The various `InstructionFormat`s are defined below.
```k
  syntax InstructionFormat ::=
      RType(opcode: RTypeOpCode, funct3: Int, funct7: Int, rd: Register, rs1: Register, rs2: Register)
    | IType(opcode: ITypeOpCode, funct3: Int, rd: Register, rs1: Register, imm: Int)
    | SType(opcode: STypeOpCode, funct3: Int, rs1: Register, rs2: Register, imm: Int)
    | BType(opcode: BTypeOpCode, funct3: Int, rs1: Register, rs2: Register, imm: Int)
    | UType(opcode: UTypeOpCode, rd: Register, imm: Int)
    | JType(opcode: JTypeOpCode, rd: Register, imm: Int)
    | UnrecognizedInstructionFormat(Int)
```
We determine the correct format by decoding the op code from the 7 least-signficant bits,
```k
  syntax OpCode ::=
      RTypeOpCode
    | ITypeOpCode
    | STypeOpCode
    | BTypeOpCode
    | UTypeOpCode
    | JTypeOpCode
    | UnrecognizedOpCode

  syntax RTypeOpCode ::=
      "OP"
  syntax ITypeOpCode ::=
      "JALR"
    | "LOAD"
    | "OP-IMM"
    | "MISC-MEM"
    | "SYSTEM"
  syntax STypeOpCode ::=
      "STORE"
  syntax BTypeOpCode ::=
      "BRANCH"
  syntax UTypeOpCode ::=
      "LUI"
    | "AUIPC"
  syntax JTypeOpCode ::=
      "JAL"
  syntax UnrecognizedOpCode ::=
      "UNRECOGNIZED"

  syntax OpCode ::= decodeOpCode(Int) [function, total]
  rule decodeOpCode(55 ) => LUI
  rule decodeOpCode(23 ) => AUIPC
  rule decodeOpCode(111) => JAL
  rule decodeOpCode(103) => JALR
  rule decodeOpCode(99 ) => BRANCH
  rule decodeOpCode(3  ) => LOAD
  rule decodeOpCode(35 ) => STORE
  rule decodeOpCode(19 ) => OP-IMM
  rule decodeOpCode(51 ) => OP
  rule decodeOpCode(15 ) => MISC-MEM
  rule decodeOpCode(115) => SYSTEM
  rule decodeOpCode(_  ) => UNRECOGNIZED [owise]
```
matching on the type of the resulting opcode,
```k
  syntax InstructionFormat ::= decode(Int) [function, total]
  rule decode(I) => decodeWithOp(decodeOpCode(I &Int 127), I >>Int 7)
```
then finally bit-fiddling to mask out the appropriate bits for each field.
```k
  syntax InstructionFormat ::= decodeWithOp(OpCode, Int) [function]

  rule decodeWithOp(OPCODE:RTypeOpCode, I) =>
    RType(OPCODE, (I >>Int 5) &Int 7, (I >>Int 18) &Int 127, I &Int 31, (I >>Int 8) &Int 31, (I >>Int 13) &Int 31)
  rule decodeWithOp(OPCODE:ITypeOpCode, I) =>
    IType(OPCODE, (I >>Int 5) &Int 7, I &Int 31, (I >>Int 8) &Int 31, (I >>Int 13) &Int 4095)
  rule decodeWithOp(OPCODE:STypeOpCode, I) =>
    SType(OPCODE, (I >>Int 5) &Int 7, (I >>Int 8) &Int 31, (I >>Int 13) &Int 31, (((I >>Int 18) &Int 127) <<Int 5) |Int (I &Int 31))
  rule decodeWithOp(OPCODE:BTypeOpCode, I) =>
    BType(OPCODE, (I >>Int 5) &Int 7, (I >>Int 8) &Int 31, (I >>Int 13) &Int 31, (((I >>Int 24) &Int 1) <<Int 11) |Int ((I &Int 1) <<Int 10) |Int (((I >>Int 18) &Int 63) <<Int 4) |Int ((I >>Int 1) &Int 15))
  rule decodeWithOp(OPCODE:UTypeOpCode, I) =>
    UType(OPCODE, I &Int 31, (I >>Int 5) &Int 1048575)
  rule decodeWithOp(OPCODE:JTypeOpCode, I) =>
    JType(OPCODE, I &Int 31, (((I >>Int 24) &Int 1) <<Int 19) |Int (((I >>Int 5) &Int 255) <<Int 11) |Int (((I >>Int 13) &Int 1) <<Int 10) |Int ((I >>Int 14) &Int 1023))
  rule decodeWithOp(_:UnrecognizedOpCode, I) =>
    UnrecognizedInstructionFormat(I)
```
Finally, we can disassemble the instruction by inspecting the fields for each format. Note that, where appropriate, we infinitely sign extend immediates to represent them as K `Int`s.
```k
  syntax Instruction ::= disassemble(InstructionFormat) [function, total]

  rule disassemble(RType(OP, 0, 0,  RD, RS1, RS2)) => ADD  RD , RS1 , RS2
  rule disassemble(RType(OP, 0, 32, RD, RS1, RS2)) => SUB  RD , RS1 , RS2
  rule disassemble(RType(OP, 1, 0,  RD, RS1, RS2)) => SLL  RD , RS1 , RS2
  rule disassemble(RType(OP, 2, 0,  RD, RS1, RS2)) => SLT  RD , RS1 , RS2
  rule disassemble(RType(OP, 3, 0,  RD, RS1, RS2)) => SLTU RD , RS1 , RS2
  rule disassemble(RType(OP, 4, 0,  RD, RS1, RS2)) => XOR  RD , RS1 , RS2
  rule disassemble(RType(OP, 5, 0,  RD, RS1, RS2)) => SRL  RD , RS1 , RS2
  rule disassemble(RType(OP, 5, 32, RD, RS1, RS2)) => SRA  RD , RS1 , RS2
  rule disassemble(RType(OP, 6, 0,  RD, RS1, RS2)) => OR   RD , RS1 , RS2
  rule disassemble(RType(OP, 7, 0,  RD, RS1, RS2)) => AND  RD , RS1 , RS2

  rule disassemble(IType(OP-IMM, 0, RD, RS1, IMM)) => ADDI  RD , RS1 , infSignExtend(IMM, 12)
  rule disassemble(IType(OP-IMM, 1, RD, RS1, IMM)) => SLLI  RD , RS1 , IMM &Int 31 requires (IMM >>Int 5) &Int 127 ==Int 0
  rule disassemble(IType(OP-IMM, 2, RD, RS1, IMM)) => SLTI  RD , RS1 , infSignExtend(IMM, 12)
  rule disassemble(IType(OP-IMM, 3, RD, RS1, IMM)) => SLTIU RD , RS1 , infSignExtend(IMM, 12)
  rule disassemble(IType(OP-IMM, 4, RD, RS1, IMM)) => XORI  RD , RS1 , infSignExtend(IMM, 12)
  rule disassemble(IType(OP-IMM, 5, RD, RS1, IMM)) => SRLI  RD , RS1 , IMM &Int 31 requires (IMM >>Int 5) &Int 127 ==Int 0
  rule disassemble(IType(OP-IMM, 5, RD, RS1, IMM)) => SRAI  RD , RS1 , IMM &Int 31 requires (IMM >>Int 5) &Int 127 ==Int 32
  rule disassemble(IType(OP-IMM, 6, RD, RS1, IMM)) => ORI   RD , RS1 , infSignExtend(IMM, 12)
  rule disassemble(IType(OP-IMM, 7, RD, RS1, IMM)) => ANDI  RD , RS1 , infSignExtend(IMM, 12)

  rule disassemble(IType(JALR, 0, RD, RS1, IMM)) => JALR RD , infSignExtend(IMM, 12) ( RS1 )

  rule disassemble(IType(LOAD, 0, RD, RS1, IMM)) => LB  RD , infSignExtend(IMM, 12) ( RS1 )
  rule disassemble(IType(LOAD, 1, RD, RS1, IMM)) => LH  RD , infSignExtend(IMM, 12) ( RS1 )
  rule disassemble(IType(LOAD, 2, RD, RS1, IMM)) => LW  RD , infSignExtend(IMM, 12) ( RS1 )
  rule disassemble(IType(LOAD, 4, RD, RS1, IMM)) => LBU RD , infSignExtend(IMM, 12) ( RS1 )
  rule disassemble(IType(LOAD, 5, RD, RS1, IMM)) => LHU RD , infSignExtend(IMM, 12) ( RS1 )

  rule disassemble(IType(MISC-MEM, 0, 0, 0, 2099)) => FENCE.TSO
  rule disassemble(IType(MISC-MEM, 0, 0, 0, IMM)) => FENCE (IMM >>Int 4) &Int 15 , IMM &Int 15 requires (IMM >>Int 8) &Int 15 ==Int 0

  rule disassemble(IType(SYSTEM, 0, 0, 0, 0)) => ECALL
  rule disassemble(IType(SYSTEM, 0, 0, 0, 1)) => EBREAK

  rule disassemble(SType(STORE, 0, RS1, RS2, IMM)) => SB RS2 , infSignExtend(IMM, 12) ( RS1 )
  rule disassemble(SType(STORE, 1, RS1, RS2, IMM)) => SH RS2 , infSignExtend(IMM, 12) ( RS1 )
  rule disassemble(SType(STORE, 2, RS1, RS2, IMM)) => SW RS2 , infSignExtend(IMM, 12) ( RS1 )

  rule disassemble(BType(BRANCH, 0, RS1, RS2, IMM)) => BEQ  RS1 , RS2 , infSignExtend(IMM, 12) *Int 2
  rule disassemble(BType(BRANCH, 1, RS1, RS2, IMM)) => BNE  RS1 , RS2 , infSignExtend(IMM, 12) *Int 2
  rule disassemble(BType(BRANCH, 4, RS1, RS2, IMM)) => BLT  RS1 , RS2 , infSignExtend(IMM, 12) *Int 2
  rule disassemble(BType(BRANCH, 5, RS1, RS2, IMM)) => BGE  RS1 , RS2 , infSignExtend(IMM, 12) *Int 2
  rule disassemble(BType(BRANCH, 6, RS1, RS2, IMM)) => BLTU RS1 , RS2 , infSignExtend(IMM, 12) *Int 2
  rule disassemble(BType(BRANCH, 7, RS1, RS2, IMM)) => BGEU RS1 , RS2 , infSignExtend(IMM, 12) *Int 2

  rule disassemble(UType(LUI, RD, IMM))   => LUI   RD , IMM
  rule disassemble(UType(AUIPC, RD, IMM)) => AUIPC RD , IMM

  rule disassemble(JType(JAL, RD, IMM)) => JAL RD , infSignExtend(IMM, 20) *Int 2

  rule disassemble(_:InstructionFormat) => INVALID_INSTR [owise]
endmodule
```
