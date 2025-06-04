module PICK-DROP0
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <regs>
        1 |-> (signExtend ( ... bits: Bytes2Int ( pickFront ( dropFront ( #bytes ( W1:Bytes +Bytes b"\x00\x00\x00\x00" ) #empty ( 4 ) #bytes ( Int2Bytes ( 4 , signExtend ( ... bits: Bytes2Int ( substrBytes ( W0:Bytes , 28 , 32 ) , LE , Unsigned ) , signBitIdx: 32 ) &Int 4294967295 , LE )  ) .SparseBytes , 20 ) , 4 ) , LE , Unsigned ) , signBitIdx: 32 ) => Bytes2Int ( substrBytes ( W1 , 20 , 24 ) , LE , Unsigned ))
    </regs>
    <pc> 0 </pc>
    <haltCond> ADDRESS ( 0 ) </haltCond>
requires lengthBytes(W0) ==Int 32 andBool lengthBytes(W1) ==Int 32
endmodule

