module PICKFRONT0
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <regs>
        .Map
    </regs>
    <pc> 0 </pc>
    <mem>
    #bytes(pickFront ( 4 , #bytes ( substrBytes ( W0:Bytes , 16 , 32 ) +Bytes W1:Bytes +Bytes b"\x00\x00\x00\x00\x00" ) .SparseBytes )) .SparseBytes
    => #bytes ( substrBytes ( W0:Bytes , 16 , 20 ) ) .SparseBytes
    </mem>
    <haltCond> ADDRESS ( 0 ) </haltCond>
requires lengthBytes(W0) ==Int 32 andBool lengthBytes(W1) ==Int 32
endmodule
