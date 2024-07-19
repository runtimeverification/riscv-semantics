```k
requires "riscv-disassemble.md"
requires "riscv-instructions.md"

module RISCV-CONFIGURATION
  imports INT
  imports MAP
  imports RANGEMAP

  syntax HaltCondition

  syntax Int ::= XLEN() [macro]
  rule XLEN() => 32

  configuration
    <riscv>
      <instrs> .K </instrs>
      <mem> $MEM:Map </mem> // Map{Int, Int}
      <regs> .Map </regs> // Map{Int, Int}
      <pc> $PC:Int </pc>
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
      "NEVER"               [symbol(HaltNever)]
    | "ADDRESS" "(" Int ")" [symbol(HaltAtAddress)]


  rule shouldHalt(NEVER) => false

  rule [[ shouldHalt(ADDRESS(END)) => true ]]
       <pc> PC </pc>
       requires END ==Int PC

  rule [[ shouldHalt(ADDRESS(END)) => false ]]
       <pc> PC </pc>
       requires END =/=Int PC
endmodule

module RISCV-MEMORY
  imports INT
  imports MAP
  imports RANGEMAP
  imports RISCV-CONFIGURATION
  imports RISCV-DISASSEMBLE
  imports RISCV-INSTRUCTIONS

  syntax Int ::= wrapAddr(address: Int) [function]
  rule wrapAddr(A) => A modInt (2 ^Int XLEN())

  syntax Int ::= loadByte(memory: Map, address: Int) [function]
  rule loadByte(MEM, ADDR) => { MEM [ wrapAddr(ADDR) ] } :>Int

  syntax Instruction ::= fetchInstr(memory: Map, address: Int) [function]
  rule fetchInstr(MEM, ADDR) =>
    disassemble((loadByte(MEM, ADDR +Int 3) <<Int 24) |Int
                (loadByte(MEM, ADDR +Int 2) <<Int 16) |Int
                (loadByte(MEM, ADDR +Int 1) <<Int 8 ) |Int
                 loadByte(MEM, ADDR       ))


  syntax Map ::= writeReg(regs: Map, rd: Int, value: Int) [function]
  rule writeReg(REGS, 0 , _  ) => REGS
  rule writeReg(REGS, RD, VAL) => REGS[RD <- VAL] requires RD =/=Int 0

  syntax Int ::= readReg(regs: Map, rs: Int) [function]
  rule readReg(_   , 0 ) => 0
  rule readReg(REGS, RS) => { REGS[RS] } :>Int requires RS =/=Int 0
endmodule

module RISCV
  imports RISCV-CONFIGURATION
  imports RISCV-DISASSEMBLE
  imports RISCV-INSTRUCTIONS
  imports RISCV-MEMORY
  imports RISCV-TERMINATION

  rule <instrs> .K => fetchInstr(MEM, PC) </instrs>
       <mem> MEM </mem>
       <pc> PC </pc>
       <halt> H </halt>
       requires notBool shouldHalt(H)

  rule <instrs> ADDI RD , RS , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, chopAndExtend(readReg(REGS, RS) +Int IMM, XLEN())) </regs>
       <pc> PC => wrapAddr(PC +Int 4) </pc>

  rule <instrs> LUI RD , IMM => .K ...</instrs>
       <regs> REGS => writeReg(REGS, RD, chopAndExtend(IMM <<Int 12, XLEN())) </regs>
       <pc> PC => wrapAddr(PC +Int 4) </pc>
endmodule
```
