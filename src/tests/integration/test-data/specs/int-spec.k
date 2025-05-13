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
    </regs>
    <test>
      <haltCond> ADDRESS ( W ( 0 ) ) </haltCond>
    </test>
endmodule