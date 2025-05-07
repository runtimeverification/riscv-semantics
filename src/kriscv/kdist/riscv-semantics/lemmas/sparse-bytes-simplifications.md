# Sparse Bytes Simplifications

This module contains lemmas specific to sparse bytes in `sparse-bytes.md`. If you want to reuse sparse bytes to build your own semantics' memory model, you can use this module to ease your symbolic execution.

## Preliminaries

```k
requires "../sparse-bytes.md"
module SPARSE-BYTES-SIMPLIFICATIONS
  imports SPARSE-BYTES
```

## readByteBF

For symbolic execution, we need to tackle the patterns of `#bytes(B +Bytes _) _` and `#bytes(B +Bytes BS) EF` to obtain as exact as possible values for `readByte`.

```k
  rule readByteBF(#bytes(B +Bytes _) _ , I) => B[ I ] 
    requires I >=Int 0 andBool I <Int lengthBytes(B) [simplification(45)]
  rule readByteBF(#bytes(B +Bytes BS) EF , I) => readByteBF(#bytes(BS) EF , I -Int lengthBytes(B)) 
    requires I >=Int lengthBytes(B) [simplification(45)]
```


## writeByteBF

To write a byte to a symbolic sparse byte region, we need to:

```k
  rule writeBytesBF(#bytes(B +Bytes BS) EF, I, V, NUM) => #bytes(replaceAtBytes(B, I, Int2Bytes(NUM, V, LE)) +Bytes BS) EF
    requires I >=Int 0 andBool I +Int NUM <=Int lengthBytes(B)  [simplification(45)]
  rule writeBytesBF(#bytes(B +Bytes BS) EF, I, V, NUM) => prepend(substrBytes(B, 0, I) +Bytes Int2Bytes(NUM, V, LE), dropFront(#bytes(BS) EF, I +Int NUM -Int lengthBytes(B)))
    requires I <Int lengthBytes(B) andBool I +Int NUM >Int lengthBytes(B)    [simplification(45)]
  rule writeBytesBF(#bytes(B +Bytes BS) EF, I, V, NUM) => prepend(B, writeBytesBF(#bytes(BS) EF, I -Int lengthBytes(B), V, NUM))
    requires I >=Int lengthBytes(B)                             [simplification(45)]
```

```k
endmodule
```
