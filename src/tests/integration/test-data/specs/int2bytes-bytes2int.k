module INT2BYTES-BYTES2INT
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <mem>
      #bytes (  Int2Bytes ( 4 , Bytes2Int ( substrBytes ( reverseBytes ( VALUE:Bytes ) , 20 , 21 ) , LE , Unsigned ) , LE ) ) .SparseBytes
      => 
      #bytes ( substrBytes ( VALUE:Bytes , 11 , 12 ) +Bytes b"\x00\x00\x00" ) .SparseBytes
    </mem>
    <pc> 0 </pc>
    <haltCond> ADDRESS ( 0 ) </haltCond>
    requires lengthBytes(VALUE) ==Int 32
endmodule
