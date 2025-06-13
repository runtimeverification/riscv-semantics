module YY
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> 0 </pc>
    <regs>
     1 |-> (Bytes2Int(Int2Bytes(1, X, LE), LE, Unsigned) => (X +Int Y +Int Z &Int 4294967295) >>Int 8 => 1)
    </regs>
    <haltCond> ADDRESS ( 0 ) </haltCond>
requires 0 <=Int X andBool 0 <=Int Y andBool 0 <=Int Z
endmodule
