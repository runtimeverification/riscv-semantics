requires "riscv-semantics/riscv.md"

module PICKFRONT0
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <regs>
        .Map
    </regs>
    <pc> W ( 0 ) </pc>
    <mem>
    #bytes(pickFront ( #bytes ( substrBytes ( W0:Bytes , 16 , 32 ) +Bytes W1:Bytes +Bytes b"\x00\x00\x00\x00\x00" ) .SparseBytes , 4 )) .SparseBytes
    => #bytes ( substrBytes ( W0:Bytes , 16 , 20 ) ) .SparseBytes
    </mem>
    <test>
      <haltCond> ADDRESS ( W ( 0 ) ) </haltCond>
    </test>
requires lengthBytes(W0) ==Int 32 andBool lengthBytes(W1) ==Int 32
endmodule
