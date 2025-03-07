# RISC-V Execution
## Configuration
The configuration is divided into two sections:
- `<riscv>`, containing the state of the abstract machine.
- `<test>`, containing any additional state needed to run tests.

The `<riscv>` section contain the following cells:
- `<instrs>`, a K-sequence denoting a pipeline of operations to be executed. Initially, we load the `#EXECUTE` operation, which indicates that instructions should be continually fetched and executed.
- `<regs>`, a map from each initialized `Register` to its current value.
- `<pc>`, the program counter register.
- `<mem>`, a map from initialized `Word` addresses to the byte stored at the address.

The `<test>` section currently contains on a single cell:
- `<haltCond>`, a value indicating under which conditions the program should be halted.
```k
requires "riscv-disassemble.md"
requires "riscv-instructions.md"
requires "sparse-bytes.md"
requires "word.md"

module RISCV-CONFIGURATION
  imports BOOL
  imports INT
  imports MAP
  imports RANGEMAP
  imports SPARSE-BYTES
  imports WORD

  syntax KItem ::= "#EXECUTE"

  configuration
    <riscv>
      <instrs> #EXECUTE ~> .K </instrs>
      <regs> .Map </regs> // Map{Register, Word}
      <pc> $PC:Word </pc>
      <mem> $MEM:SparseBytes </mem>
    </riscv>
    <test>
      <haltCond> $HALT:HaltCondition </haltCond>
    </test>

  syntax HaltCondition
endmodule
```

## Termination
RISC-V does not provide a `halt` instruction or equivalent, instead relying on the surrounding environment, e.g., making a sys-call to exit with a particular exit code.
As we do not model the surrounding environment, for testing purposes we add our own custom halting mechanism denoted by a `HaltCondition` value.

This is done with three components:
- A `HaltCondition` value stored in the configuation indicating under which conditions we should halt.
- A `#CHECK_HALT` operation indicating that the halt condition should be checked.
- A `#HALT` operation which terminates the simulation by consuming all following operations in the pipeline without executing them.
```k
module RISCV-TERMINATION
  imports RISCV-CONFIGURATION
  imports BOOL
  imports INT

  syntax KItem ::=
      "#HALT"
    | "#CHECK_HALT"

  rule <instrs> #HALT ~> (_ => .K) ...</instrs>

  syntax HaltCondition ::=
      "NEVER"                [symbol(HaltNever)]
    | "ADDRESS" "(" Word ")" [symbol(HaltAtAddress)]
```
The `NEVER` condition indicates that we should never halt.
```k
  rule <instrs> #CHECK_HALT => .K ...</instrs>
       <haltCond> NEVER </haltCond>
```
The `ADDRESS(_)` condition indicates that we should halt if the `PC` reaches a particular address.
```k
  rule <instrs> #CHECK_HALT => #HALT ...</instrs>
       <pc> PC </pc>
       <haltCond> ADDRESS(END) </haltCond>
       requires PC ==Word END

  rule <instrs> #CHECK_HALT => .K ...</instrs>
       <pc> PC </pc>
       <haltCond> ADDRESS(END) </haltCond>
       requires PC =/=Word END
endmodule
```

## Memory and Registers
RISC-V uses a circular, byte-adressable memory space containing `2^XLEN` bytes.
```k
module RISCV-MEMORY
  imports INT
  imports MAP
  imports RANGEMAP
  imports RISCV-CONFIGURATION
  imports RISCV-DISASSEMBLE
  imports RISCV-INSTRUCTIONS
  imports WORD

  syntax Memory = SparseBytes
```
We abstract the particular memory representation behind `loadByte` and `storeByte` functions.
```k
  syntax Int ::= loadByte(memory: Memory, address: Word) [function, symbol(Memory:loadByte)]
  rule loadByte(MEM, W(ADDR)) => MaybeByte2Int(readByte(MEM, ADDR))

  syntax Memory ::= storeByte(memory: Memory, address: Word, byte: Int) [function, total, symbol(Memory:storeByte)]
  rule storeByte(MEM, W(ADDR), B) => writeByte(MEM, ADDR, B)
```
For multi-byte loads and stores, we presume a little-endian architecture.
```k
  syntax Int ::= loadBytes(memory: Memory, address: Word, numBytes: Int) [function]
  rule loadBytes(MEM, ADDR, 1  ) => loadByte(MEM, ADDR)
  rule loadBytes(MEM, ADDR, NUM) => (loadBytes(MEM, ADDR +Word W(1), NUM -Int 1) <<Int 8) |Int loadByte(MEM, ADDR) requires NUM >Int 1

  syntax Memory ::= storeBytes(memory: Memory, address: Word, bytes: Int, numBytes: Int) [function]
  rule storeBytes(MEM, ADDR, BS, 1  ) => storeByte(MEM, ADDR, BS)
  rule storeBytes(MEM, ADDR, BS, NUM) => storeBytes(storeByte(MEM, ADDR, BS &Int 255), ADDR +Word W(1), BS >>Int 8, NUM -Int 1) requires NUM >Int 1
```
Instructions are always 32-bits, and are stored in little-endian format regardless of the endianness of the overall architecture.
```k
  syntax Instruction ::= fetchInstr(memory: Memory, address: Word) [function]
  rule fetchInstr(MEM, ADDR) =>
    disassemble((loadByte(MEM, ADDR +Word W(3)) <<Int 24) |Int
                (loadByte(MEM, ADDR +Word W(2)) <<Int 16) |Int
                (loadByte(MEM, ADDR +Word W(1)) <<Int 8 ) |Int
                 loadByte(MEM, ADDR       ))
```
Registers should be manipulated with the `writeReg` and `readReg` functions, which account for `x0` always being hard-wired to contain all `0`s.
```k
  syntax Map ::= writeReg(regs: Map, rd: Int, value: Word) [function]
  rule writeReg(REGS, 0 , _  ) => REGS
  rule writeReg(REGS, RD, VAL) => REGS[RD <- VAL] [owise]

  syntax Word ::= readReg(regs: Map, rs: Int) [function]
  rule readReg(_   , 0 ) => W(0)
  rule readReg(REGS, RS) => { REGS[RS] } :>Word [owise]
endmodule
```

## Instruction Execution
The `RISCV` module contains the actual rules to fetch and execute instructions.
```k
module RISCV
  imports RISCV-CONFIGURATION
  imports RISCV-DISASSEMBLE
  imports RISCV-INSTRUCTIONS
  imports RISCV-MEMORY
  imports RISCV-TERMINATION
  imports WORD
```
`#EXECUTE` indicates that we should continuously fetch and execute instructions, loading the instruction into the `#NEXT[_]` operator.
```k
  syntax KItem ::= "#NEXT" "[" Instruction "]"

  rule <instrs> (.K => #NEXT[ fetchInstr(MEM, PC) ]) ~> #EXECUTE ...</instrs>
       <pc> PC </pc>
       <mem> MEM </mem>
```
`#NEXT[ I ]` sets up the pipeline to execute the the fetched instruction.
```k
  rule <instrs> #NEXT[ I ] => I ~> #PC[ I ] ~> #CHECK_HALT ...</instrs>
```
`#PC[ I ]` updates the `PC` as needed to fetch the next instruction after executing `I`. For most instructions, this increments `PC` by the width of the instruction (always `4` bytes in the base ISA). For branch and jump instructions, which already manually update the `PC`, this is a no-op.
```k
  syntax KItem ::= "#PC" "[" Instruction "]"

  rule <instrs> #PC[ I ] => .K ...</instrs>
       <pc> PC => PC +Word pcIncrAmount(I) </pc>

  syntax Word ::= pcIncrAmount(Instruction) [function, total]
  rule pcIncrAmount(BEQ _ , _ , _   ) => W(0)
  rule pcIncrAmount(BNE _ , _ , _   ) => W(0)
  rule pcIncrAmount(BLT _ , _ , _   ) => W(0)
  rule pcIncrAmount(BLTU _ , _ , _  ) => W(0)
  rule pcIncrAmount(BGE _ , _ , _   ) => W(0)
  rule pcIncrAmount(BGEU _ , _ , _  ) => W(0)
  rule pcIncrAmount(JAL _ , _       ) => W(0)
  rule pcIncrAmount(JALR _ , _ ( _ )) => W(0)
  rule pcIncrAmount(_)                => W(4) [owise]
```
We then provide rules to consume and execute each instruction from the top of the pipeline.

`ADDI` adds the immediate `IMM` to the value in register `RS`, storing the result in register `RD`. Note that we must use `chop` to convert `IMM` from an infinitely sign-extended K `Int` to an `XLEN`-bit `Word`.
```k
  rule <instrs> ADDI RD , RS , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) +Word chop(IMM)) </regs>
```
`SLTI` treats the value in `RS` as a signed two's complement and compares it to `IMM`, writing `1` to `RD` if `RS` is less than `IMM` and `0` otherwise.
```k
  rule <instrs> SLTI RD , RS , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, Bool2Word(readReg(REGS, RS) <sWord chop(IMM))) </regs>
```
`SLTIU` proceeds analogously, but treating `RS` and `IMM` as XLEN-bit unsigned integers.
```k
  rule <instrs> SLTIU RD , RS , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, Bool2Word(readReg(REGS, RS) <uWord chop(IMM))) </regs>
```
`ADDI`, `ORI`, and `XORI` perform bitwise operations between `RS` and `IMM`, storing the result in `RD`.
```k
  rule <instrs> ANDI RD , RS , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) &Word chop(IMM)) </regs>

  rule <instrs> ORI RD , RS , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) |Word chop(IMM)) </regs>

  rule <instrs> XORI RD , RS , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) xorWord chop(IMM)) </regs>
```
`SLLI`, `SRLI`, and `SRAI` perform logical left, logical right, and arithmetic right shifts respectively.
```k
  rule <instrs> SLLI RD , RS , SHAMT => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) <<Word SHAMT) </regs>

  rule <instrs> SRLI RD , RS , SHAMT => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) >>lWord SHAMT) </regs>

  rule <instrs> SRAI RD , RS , SHAMT => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) >>aWord SHAMT) </regs>
```
`LUI` builds a 32-bit constant from the 20-bit immediate by setting the 12 least-significant bits to `0`, then sign extends to `XLEN` bits and places the result in register `RD`.
```k
  rule <instrs> LUI RD , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, signExtend(IMM <<Int 12, 32)) </regs>
```
`AUIPC` proceeds similarly to `LUI`, but adding the sign-extended constant to the current `PC` before placing the result in `RD`.
```k
  rule <instrs> AUIPC RD , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, PC +Word signExtend(IMM <<Int 12, 32)) </regs>
       <pc> PC </pc>
```
The following instructions behave analogously to their `I`-suffixed counterparts, but taking their second argument from an `RS2` register rather than an immediate.
```k
  rule <instrs> ADD RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) +Word readReg(REGS, RS2)) </regs>

  rule <instrs> SUB RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) -Word readReg(REGS, RS2)) </regs>

  rule <instrs> SLT RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, Bool2Word(readReg(REGS, RS1) <sWord readReg(REGS, RS2))) </regs>

  rule <instrs> SLTU RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, Bool2Word(readReg(REGS, RS1) <uWord readReg(REGS, RS2))) </regs>

  rule <instrs> AND RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) &Word readReg(REGS, RS2)) </regs>

  rule <instrs> OR RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) |Word readReg(REGS, RS2)) </regs>

  rule <instrs> XOR RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) xorWord readReg(REGS, RS2)) </regs>
```
`MUL` gives the lowest `XLEN` bits after multiplication.
```k
  rule <instrs> MUL RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) *Word readReg(REGS, RS2)) </regs>
```
`SLL`, `SRL`, and `SRA` read their shift amount fom the lowest `log_2(XLEN)` bits of `RS2`.
```k
  rule <instrs> SLL RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) <<Word Word2UInt(readReg(REGS, RS2) &Word W(XLEN -Int 1))) </regs>

  rule <instrs> SRL RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) >>lWord Word2UInt(readReg(REGS, RS2) &Word W(XLEN -Int 1))) </regs>

  rule <instrs> SRA RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) >>aWord Word2UInt(readReg(REGS, RS2) &Word W(XLEN -Int 1))) </regs>
```
`JAL` stores `PC + 4` in `RD`, then increments `PC` by `OFFSET`.
```k
  rule <instrs> JAL RD, OFFSET => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, PC +Word W(4)) </regs>
       <pc> PC => PC +Word chop(OFFSET) </pc>
```
`JALR` stores `PC + 4` in `RD`, sets `PC` to the value in register `RS1` plus `OFFSET`, then sets the least-significant bit of this new `PC` to `0`.
```k
  rule <instrs> JALR RD, OFFSET ( RS1 ) => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, PC +Word W(4)) </regs>
       <pc> PC => (readReg(REGS, RS1) +Word chop(OFFSET)) &Word chop(-1 <<Int 1) </pc>
```
`BEQ` increments `PC` by `OFFSET` so long as the values in registers `RS1` and `RS2` are equal. Otherwise, `PC` is incremented by `4`.
```k
  syntax Word ::= branchPC(oldPC: Word, offset: Int, branchCond: Bool) [function, total]
  rule branchPC(PC,  OFFSET, COND) => PC +Word chop(OFFSET) requires COND
  rule branchPC(PC, _OFFSET, COND) => PC +Word W(4)         requires notBool COND

  rule <instrs> BEQ RS1 , RS2 , OFFSET => .K ...</instrs>
       <regs> REGS </regs>
       <pc> PC => branchPC(PC, OFFSET, readReg(REGS, RS1) ==Word readReg(REGS, RS2)) </pc>
```
The remaining branch instructions proceed analogously, but performing different comparisons between `RS1` and `RS2`.
```k
  rule <instrs> BNE RS1 , RS2 , OFFSET => .K ...</instrs>
       <regs> REGS </regs>
       <pc> PC => branchPC(PC, OFFSET, readReg(REGS, RS1) =/=Word readReg(REGS, RS2)) </pc>

  rule <instrs> BLT RS1 , RS2 , OFFSET => .K ...</instrs>
       <regs> REGS </regs>
       <pc> PC => branchPC(PC, OFFSET, readReg(REGS, RS1) <sWord readReg(REGS, RS2)) </pc>

  rule <instrs> BGE RS1 , RS2 , OFFSET => .K ...</instrs>
       <regs> REGS </regs>
       <pc> PC => branchPC(PC, OFFSET, readReg(REGS, RS1) >=sWord readReg(REGS, RS2)) </pc>

  rule <instrs> BLTU RS1 , RS2 , OFFSET => .K ...</instrs>
       <regs> REGS </regs>
       <pc> PC => branchPC(PC, OFFSET, readReg(REGS, RS1) <uWord readReg(REGS, RS2)) </pc>

  rule <instrs> BGEU RS1 , RS2 , OFFSET => .K ...</instrs>
       <regs> REGS </regs>
       <pc> PC => branchPC(PC, OFFSET, readReg(REGS, RS1) >=uWord readReg(REGS, RS2)) </pc>
```
`LB`, `LH`, and `LW` load `1`, `2`, and `4` bytes respectively from the memory address which is `OFFSET` greater than the value in register `RS1`, then sign extends the loaded bytes and places them in register `RD`.
```k
  rule <instrs> LB RD , OFFSET ( RS1 ) => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, signExtend(loadByte(MEM, readReg(REGS, RS1) +Word chop(OFFSET)), 8)) </regs>
       <mem> MEM </mem>

  rule <instrs> LH RD , OFFSET ( RS1 ) => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, signExtend(loadBytes(MEM, readReg(REGS, RS1) +Word chop(OFFSET), 2), 16)) </regs>
       <mem> MEM </mem>

  rule <instrs> LW RD , OFFSET ( RS1 ) => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, signExtend(loadBytes(MEM, readReg(REGS, RS1) +Word chop(OFFSET), 4), 32)) </regs>
       <mem> MEM </mem>
```
`LBU` and `LHU` are analogous to `LB` and `LH`, but zero-extending rather than sign-extending.
```k
   rule <instrs> LBU RD , OFFSET ( RS1 ) => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, W(loadByte(MEM, readReg(REGS, RS1) +Word chop(OFFSET)))) </regs>
       <mem> MEM </mem>

  rule <instrs> LHU RD , OFFSET ( RS1 ) => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, W(loadBytes(MEM, readReg(REGS, RS1) +Word chop(OFFSET), 2))) </regs>
       <mem> MEM </mem>
```
Dually, `SB`, `SH`, and `SW` store the least-significant `1`, `2`, and `4` bytes respectively from `RS2` to the memory address which is `OFFSET` greater than the value in register `RS1`.
```k
  rule <instrs> SB RS2 , OFFSET ( RS1 ) => .K ...</instrs>
       <regs> REGS </regs>
       <mem> MEM => storeByte(MEM, readReg(REGS, RS1) +Word chop(OFFSET), Word2UInt(readReg(REGS, RS2)) &Int 255) </mem>

  rule <instrs> SH RS2 , OFFSET ( RS1 ) => .K ...</instrs>
       <regs> REGS </regs>
       <mem> MEM => storeBytes(MEM, readReg(REGS, RS1) +Word chop(OFFSET), Word2UInt(readReg(REGS, RS2)) &Int 65535, 2) </mem>

  rule <instrs> SW RS2 , OFFSET ( RS1 ) => .K ...</instrs>
       <regs> REGS </regs>
       <mem> MEM => storeBytes(MEM, readReg(REGS, RS1) +Word chop(OFFSET), Word2UInt(readReg(REGS, RS2)) &Int 4294967295, 4) </mem>
```
We presume a single hart with exclusive access to memory, so `FENCE` and `FENCE.TSO` are no-ops.
```k
   rule <instrs> FENCE _PRED, _SUCC => .K ...</instrs>

   rule <instrs> FENCE.TSO => .K ...</instrs>
```
As we do not model the external execution environment, we leave the `ECALL` and `EBREAK` instructions unevaluated.
```k
endmodule
```
