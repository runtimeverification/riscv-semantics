requires "riscv-semantics/riscv.md"

module BYTES2INT-INT2BYTES
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> W ( 0 ) </pc>
    <mem>
      #bytes ( Int2Bytes ( 4 , Word2UInt ( signExtend ( ... bits: Bytes2Int ( substrBytes ( W0:Bytes , 12 , 16 ) , LE , Unsigned ) , signBitIdx: 32 ) <<Word W ( 24 ) |Word signExtend ( ... bits: Bytes2Int ( substrBytes ( W0:Bytes , 12 , 16 ) , LE , Unsigned ) , signBitIdx: 32 ) &Word W ( 65280 ) <<Word W ( 8 ) |Word signExtend ( ... bits: Bytes2Int ( substrBytes ( W0:Bytes , 12 , 16 ) , LE , Unsigned ) , signBitIdx: 32 ) >>lWord W ( 8 ) &Word W ( 65280 ) |Word signExtend ( ... bits: Bytes2Int ( substrBytes ( W0:Bytes , 12 , 16 ) , LE , Unsigned ) , signBitIdx: 32 ) >>lWord W ( 24 ) ) &Int 4294967295 , LE ) ) .SparseBytes => .SparseBytes
    </mem>
    <test>
      <haltCond> ADDRESS ( W ( 0 ) ) </haltCond>
    </test>
requires lengthBytes(W0) ==Int 32 andBool lengthBytes(W1) ==Int 32
endmodule

