# RISC-V Execution
## Configuration
The configuration is divided into two sections:
- `<riscv>`, containing the state of the abstract machine
- `<test>`, containing any additional state needed to run tests

The `<riscv>` section contain the following cells:
- `<instrs>`, a K-sequence of fetched instruction to be executed
- `<regs>`, a map from each initialized `Register` to its current value
- `<pc>`, the program counter register
- `<mem>`, a map from initialized `Word` addresses to the byte stored at the address

The `<test>` section currently contains on a single cell:
- `<haltCond>`, a value indicating under which conditions the program should be halted
- `<halt>`, whether to halt the program
```k
requires "riscv-disassemble.md"
requires "riscv-instructions.md"
requires "word.md"

module RISCV-CONFIGURATION
  imports BOOL
  imports INT
  imports MAP
  imports RANGEMAP
  imports WORD

  syntax HaltCondition

  configuration
    <riscv>
      <instrs> .K </instrs>
      <regs> .Map </regs> // Map{Register, Word}
      <pc> $PC:Word </pc>
      <mem> $MEM:Map </mem> // Map{Word, Int}
    </riscv>
    <test>
      <haltCond> $HALT:HaltCondition </haltCond>
      <halt> false:Bool </halt>
    </test>
endmodule
```

## Termination
RISC-V does not provide a `halt` instruction,  instead relying on the surrounding environment, e.g., making a sys-call to exit with a particular exit code.
For testing purposes, we then add our own custom halting mechanism denoted by a `HaltCondition` value.

Currently, we support:
- Never halting unless a trap or exception is reached
- Halting when the `PC` reaches a particular address
```k
module RISCV-TERMINATION
  imports RISCV-CONFIGURATION
  imports BOOL
  imports INT

  syntax Instruction ::= "CHECK_HALT"

  syntax HaltCondition ::=
      "NEVER"                [symbol(HaltNever)]
    | "ADDRESS" "(" Word ")" [symbol(HaltAtAddress)]

  rule <instrs> CHECK_HALT => .K ...</instrs>
       <haltCond> NEVER </haltCond>
       <halt> false </halt>

  rule <instrs> CHECK_HALT => .K ...</instrs>
       <pc> PC </pc>
       <haltCond> ADDRESS(END) </haltCond>
       <halt> false => PC ==Word END </halt>
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
```
We abstract the particular memory representation behind a `loadByte` function which return the byte stored at a particular address.
```k
  syntax Int ::= loadByte(memory: Map, address: Word) [function]
  rule loadByte(MEM, ADDR) => { MEM[ADDR] } :>Int
```
Instructions are always 32-bits, and are stored in little-endian format regardless of the endianness of the overall architecture.
```k
  syntax Instruction ::= fetchInstr(memory: Map, address: Word) [function]
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
The actual execution semantics has two components:
- The instruction fetch cycle, which disassembles an instruction from the current `PC` so long as the `HaltCondition` fails, placing it into the `<instrs>` cell
- Rules to implement each instruction, removing the instruction from the top of the `<instrs>` cell and updating any state as necessary.
```k
module RISCV
  imports RISCV-CONFIGURATION
  imports RISCV-DISASSEMBLE
  imports RISCV-INSTRUCTIONS
  imports RISCV-MEMORY
  imports RISCV-TERMINATION
  imports WORD

  rule <instrs> .K => fetchInstr(MEM, PC) ~> CHECK_HALT </instrs>
       <pc> PC </pc>
       <mem> MEM </mem>
       <halt> false </halt>
```
`ADDI` adds the immediate `IMM` to the value in register `RS`, storing the result in register `RD`. Note that we must use `chop` to convert `IMM` from an infinitely sign-extended K `Int` to an `XLEN`-bit `Word`.
```k
  rule <instrs> ADDI RD , RS , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) +Word chop(IMM)) </regs>
       <pc> PC => PC +Word W(4) </pc>
```
`SLTI` treats the value in `RS` as a signed two's complement and compares it to `IMM`, writing `1` to `RD` if `RS` is less than `IMM` and `0` otherwise.
```k
  rule <instrs> SLTI RD , RS , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, Bool2Word(readReg(REGS, RS) <sWord chop(IMM))) </regs>
       <pc> PC => PC +Word W(4) </pc>
```
`SLTIU` proceeds analogously, but treating `RS` and `IMM` as XLEN-bit unsigned integers.
```k
  rule <instrs> SLTIU RD , RS , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, Bool2Word(readReg(REGS, RS) <uWord chop(IMM))) </regs>
       <pc> PC => PC +Word W(4) </pc>
```
`ADDI`, `ORI`, and `XORI` perform bitwise operations between `RS` and `IMM`, storing the result in `RD`.
```k
  rule <instrs> ANDI RD , RS , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) &Word chop(IMM)) </regs>
       <pc> PC => PC +Word W(4) </pc>

  rule <instrs> ORI RD , RS , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) |Word chop(IMM)) </regs>
       <pc> PC => PC +Word W(4) </pc>

  rule <instrs> XORI RD , RS , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) xorWord chop(IMM)) </regs>
       <pc> PC => PC +Word W(4) </pc>
```
`SLLI`, `SRLI`, and `SRAI` perform logical left, logical right, and arithmetic right shifts respectively.
```k
  rule <instrs> SLLI RD , RS , SHAMT => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) <<Word SHAMT) </regs>
       <pc> PC => PC +Word W(4) </pc>

  rule <instrs> SRLI RD , RS , SHAMT => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) >>lWord SHAMT) </regs>
       <pc> PC => PC +Word W(4) </pc>

  rule <instrs> SRAI RD , RS , SHAMT => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) >>aWord SHAMT) </regs>
       <pc> PC => PC +Word W(4) </pc>
```
`LUI` builds a 32-bit constant from the 20-bit immediate by setting the 12 least-significant bits to `0`, then sign extends to `XLEN` bits and places the result in register `RD`.
```k
  rule <instrs> LUI RD , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, signExtend(IMM <<Int 12, 32)) </regs>
       <pc> PC => PC +Word W(4) </pc>
```
`AUIPC` proceeds similarly to `LUI`, but adding the sign-extended constant to the current `PC` before placing the result in `RD`.
```k
  rule <instrs> AUIPC RD , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, PC +Word signExtend(IMM <<Int 12, 32)) </regs>
       <pc> PC => PC +Word W(4) </pc>
```
The following instructions behave analogously to their `I`-suffixed counterparts, but taking their second argument from an `RS2` register rather than an immediate.
```k
  rule <instrs> ADD RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) +Word readReg(REGS, RS2)) </regs>
       <pc> PC => PC +Word W(4) </pc>

  rule <instrs> SUB RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) -Word readReg(REGS, RS2)) </regs>
       <pc> PC => PC +Word W(4) </pc>

  rule <instrs> SLT RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, Bool2Word(readReg(REGS, RS1) <sWord readReg(REGS, RS2))) </regs>
       <pc> PC => PC +Word W(4) </pc>

  rule <instrs> SLTU RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, Bool2Word(readReg(REGS, RS1) <uWord readReg(REGS, RS2))) </regs>
       <pc> PC => PC +Word W(4) </pc>

  rule <instrs> AND RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) &Word readReg(REGS, RS2)) </regs>
       <pc> PC => PC +Word W(4) </pc>

  rule <instrs> OR RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) |Word readReg(REGS, RS2)) </regs>
       <pc> PC => PC +Word W(4) </pc>

  rule <instrs> XOR RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) xorWord readReg(REGS, RS2)) </regs>
       <pc> PC => PC +Word W(4) </pc>
```
`SLL`, `SRL`, and `SRA` read their shift amount fom the lowest `log_2(XLEN)` bits of `RS2`.
```k
  rule <instrs> SLL RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) <<Word Word2UInt(readReg(REGS, RS2) &Word W(XLEN -Int 1))) </regs>
       <pc> PC => PC +Word W(4) </pc>

  rule <instrs> SRL RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) >>lWord Word2UInt(readReg(REGS, RS2) &Word W(XLEN -Int 1))) </regs>
       <pc> PC => PC +Word W(4) </pc>

  rule <instrs> SRA RD , RS1 , RS2 => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS1) >>aWord Word2UInt(readReg(REGS, RS2) &Word W(XLEN -Int 1))) </regs>
       <pc> PC => PC +Word W(4) </pc>
```
`JAL` stores `PC + 4` in `RD`, then increments `PC` by `OFFSET`.
```k
  rule <instrs> JAL RD, OFFSET => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, PC +Word W(4)) </regs>
       <pc> PC => PC +Word chop(OFFSET) </pc>
endmodule
```
