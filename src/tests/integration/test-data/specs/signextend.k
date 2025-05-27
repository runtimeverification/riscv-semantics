requires "riscv-semantics/riscv.md"

module SIGNEXTEND
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> 0 </pc>
    <regs>
     1 |-> (Bytes2Int (b"\xff\xff\xff\xff", LE, Unsigned) => 4294967295)
     2 |-> (signExtend (Bytes2Int (b"\xff\xff\xff\xff", LE, Unsigned), 32) => 4294967295)
     3 |-> (signExtend (Bytes2Int (substrBytes(W0:Bytes, 4, 8), LE, Unsigned) , 32) => Bytes2Int(substrBytes(W0:Bytes ,4 , 8), LE, Unsigned ))
    </regs>
    <haltCond> ADDRESS ( 0 ) </haltCond>
  requires lengthBytes(W0) ==Int 32
endmodule
