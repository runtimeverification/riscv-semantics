```k
requires "riscv-disassemble.md"
requires "riscv-instructions.md"
requires "word.md"

module RISCV-CONFIGURATION
  imports INT
  imports MAP
  imports RANGEMAP
  imports WORD

  syntax HaltCondition

  configuration
    <riscv>
      <instrs> .K </instrs>
      <regs> .Map </regs> // Map{Int, Word}
      <pc> $PC:Word </pc>
      <mem> $MEM:Map </mem> // Map{Word, Int}
    </riscv>
    <test>
      <halt> $HALT:HaltCondition </halt>
    </test>
endmodule

module RISCV-TERMINATION
  imports RISCV-CONFIGURATION
  imports BOOL
  imports INT

  syntax Bool ::= shouldHalt(HaltCondition) [function]
  syntax HaltCondition ::=
      "NEVER"                [symbol(HaltNever)]
    | "ADDRESS" "(" Word ")" [symbol(HaltAtAddress)]


  rule shouldHalt(NEVER) => false

  rule [[ shouldHalt(ADDRESS(END)) => true ]]
       <pc> PC </pc>
       requires END ==Word PC

  rule [[ shouldHalt(ADDRESS(END)) => false ]]
       <pc> PC </pc>
       requires END =/=Word PC
endmodule

module RISCV-MEMORY
  imports INT
  imports MAP
  imports RANGEMAP
  imports RISCV-CONFIGURATION
  imports RISCV-DISASSEMBLE
  imports RISCV-INSTRUCTIONS
  imports WORD

  syntax Int ::= loadByte(memory: Map, address: Word) [function]
  rule loadByte(MEM, ADDR) => { MEM[ADDR] } :>Int

  syntax Instruction ::= fetchInstr(memory: Map, address: Word) [function]
  rule fetchInstr(MEM, ADDR) =>
    disassemble((loadByte(MEM, ADDR +Word W(3)) <<Int 24) |Int
                (loadByte(MEM, ADDR +Word W(2)) <<Int 16) |Int
                (loadByte(MEM, ADDR +Word W(1)) <<Int 8 ) |Int
                 loadByte(MEM, ADDR       ))

  syntax Map ::= writeReg(regs: Map, rd: Int, value: Word) [function]
  rule writeReg(REGS, 0 , _  ) => REGS
  rule writeReg(REGS, RD, VAL) => REGS[RD <- VAL] [owise]

  syntax Word ::= readReg(regs: Map, rs: Int) [function]
  rule readReg(_   , 0 ) => W(0)
  rule readReg(REGS, RS) => { REGS[RS] } :>Word [owise]
endmodule

module RISCV
  imports RISCV-CONFIGURATION
  imports RISCV-DISASSEMBLE
  imports RISCV-INSTRUCTIONS
  imports RISCV-MEMORY
  imports RISCV-TERMINATION
  imports WORD

  rule <instrs> .K => fetchInstr(MEM, PC) </instrs>
       <pc> PC </pc>
       <halt> H </halt>
       <mem> MEM </mem>
       requires notBool shouldHalt(H)

  rule <instrs> ADDI RD , RS , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, readReg(REGS, RS) +Word chop(IMM)) </regs>
       <pc> PC => PC +Word W(4) </pc>

  rule <instrs> LUI RD , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, W(IMM <<Int 12)) </regs>
       <pc> PC => PC +Word W(4) </pc>
endmodule
```
