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
      <mem> $MEM:RangeMap </mem>
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
  imports BYTES
  imports INT
  imports RANGEMAP
  imports RISCV-CONFIGURATION
  imports RISCV-DISASSEMBLE
  imports RISCV-INSTRUCTIONS

  syntax Int ::= loadByte(address: Int) [function]
  rule [[ loadByte(ADDR) => ({ MEM [ ADDR ] } :>Bytes) [ #let ([ S , _ ) :Range) = find_range(MEM, ADDR) #in ADDR -Int S ] ]]
       <mem> MEM </mem>

  syntax Int ::= wrapAddr(address: Int) [function]
  rule wrapAddr(A) => A modInt (2 ^Int XLEN())

  syntax Instruction ::= fetchInstr(address: Int) [function]
  rule fetchInstr(ADDR) =>
    disassemble((loadByte(ADDR +Int 3) <<Int 24) |Int
                (loadByte(ADDR +Int 2) <<Int 16) |Int
                (loadByte(ADDR +Int 1) <<Int 8 ) |Int
                 loadByte(ADDR       ))


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

  rule <instrs> .K => fetchInstr(PC) </instrs>
       <pc> PC </pc>
       <halt> H </halt>
       requires notBool shouldHalt(H)
endmodule
```
