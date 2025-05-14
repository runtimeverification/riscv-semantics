requires "riscv-semantics/riscv.md"

module BYTES-INT
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> W ( 0 ) </pc>
    <regs>
     6 |-> (W(Bytes2Int(Int2Bytes ( 4 , Bytes2Int (W1, LE, Unsigned), LE ), LE, Unsigned)) => W(Bytes2Int(W1, LE, Unsigned)))
     7 |-> (W(Bytes2Int(Int2Bytes ( 4 , Bytes2Int ( substrBytes ( W0:Bytes , 31 , 32 ) +Bytes substrBytes ( W0:Bytes , 30 , 31 ) +Bytes substrBytes ( W0:Bytes , 29 , 30 ) +Bytes substrBytes ( W0:Bytes , 28 , 32 ) , LE , Unsigned ) , LE ), LE, Unsigned)) => W(Bytes2Int(substrBytes ( W0:Bytes , 31 , 32 ) +Bytes substrBytes ( W0:Bytes , 30 , 31 ) +Bytes substrBytes ( W0:Bytes , 29 , 30 ) +Bytes substrBytes ( W0:Bytes , 28 , 29), LE, Unsigned)))
    </regs>
    <test>
      <haltCond> ADDRESS ( W ( 0 ) ) </haltCond>
    </test>
requires lengthBytes(W0) ==Int 32
 andBool lengthBytes(W1) ==Int 4
endmodule