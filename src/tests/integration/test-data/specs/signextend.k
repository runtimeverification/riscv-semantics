requires "riscv-semantics/riscv.md"

module SIGNEXTEND
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> W ( 0 ) </pc>
    <regs>
     1 |-> (W(Bytes2Int (b"\xff\xff\xff\xff", LE, Unsigned)) => W(4294967295))
     2 |-> (signExtend (Bytes2Int (b"\xff\xff\xff\xff", LE, Unsigned), 32) => W(4294967295))
     3 |-> (signExtend (Bytes2Int (substrBytes(W0:Bytes, 4, 8), LE, Unsigned) , 32) => W(Bytes2Int(substrBytes(W0:Bytes ,4 , 8), LE, Unsigned )))
    </regs>
    <test>
      <haltCond> ADDRESS ( W ( 0 ) ) </haltCond>
    </test>
// requires lengthBytes(W0) ==Int 32
endmodule