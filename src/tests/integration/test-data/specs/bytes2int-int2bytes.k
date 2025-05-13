requires "riscv-semantics/riscv.md"

module BYTES2INT-INT2BYTES
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> W ( 0 ) </pc>
    <mem>
      #bytes ( Int2Bytes ( 4 , Bytes2Int ( substrBytes ( W0:Bytes , 28 , 32 ) , LE , Unsigned ) <<Int 24 &Int 4294967295 |Int Bytes2Int ( substrBytes ( W0:Bytes , 28 , 32 ) , LE , Unsigned ) &Int 65280 <<Int 8 &Int 4294967295 |Int Bytes2Int ( substrBytes ( W0:Bytes , 28 , 32 ) , LE , Unsigned ) >>Int 8 &Int 65280 |Int Bytes2Int ( substrBytes ( W0:Bytes , 28 , 32 ) , LE , Unsigned ) >>Int 24 &Int 4294967295 , LE ) ) .SparseBytes => .SparseBytes
    </mem>
    <test>
      <haltCond> ADDRESS ( W ( 0 ) ) </haltCond>
    </test>
requires lengthBytes(W0) ==Int 32 andBool lengthBytes(W1) ==Int 32
endmodule

