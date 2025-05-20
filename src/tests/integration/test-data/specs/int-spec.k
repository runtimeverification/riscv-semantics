requires "riscv-semantics/riscv.md"

module INT-SPEC
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> W ( 0 ) </pc>
    <regs>
     1 |-> (W(12 <<Int 8 <<Int 8) => W(786432))
     2 |-> (W(12 <<Int 16) => W(786432))
     3 |-> (W(W0 <<Int 8 <<Int 8) => W(W0 <<Int 16))
     4 |-> (W(W1 &Int 4294967295) => W(W1))
     5 |-> (W(W2 <<Int 16 &Int 4294967295) => W(W2 <<Int 16))
     6 |-> (W(W3[0] <<Int 16 &Int 4294967295) => W(W3[0] <<Int 16))
    </regs>
    <test>
      <haltCond> ADDRESS ( W ( 0 ) ) </haltCond>
    </test>
requires 0 <=Int W1 andBool W1 <Int 4294967295
 andBool 0 <=Int W2 andBool W2 <Int 256
 andBool lengthBytes(W3) ==Int 32
endmodule