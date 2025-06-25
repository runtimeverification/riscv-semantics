# Sparse Bytes Simplifications

This module contains lemmas specific to sparse bytes in `sparse-bytes.md`. If you want to reuse sparse bytes to build your own semantics' memory model, you can use this module to ease your symbolic execution.

## Preliminaries

```k
requires "../sparse-bytes.md"
module SPARSE-BYTES-SIMPLIFICATIONS
  imports SPARSE-BYTES
```

## pickFront and dropFront

For symbolic execution, we need to tackle the patterns of `#bytes(B +Bytes _) _` and `#bytes(B +Bytes BS) EF` to obtain as exact as possible values for `pickFront`.

```k
  rule pickFront(J0, #bytes(substrBytes(B, I, J) +Bytes _) _) => substrBytes(substrBytes(B, I, J), 0, J0)
    requires 0 <=Int I andBool I <=Int J andBool J <=Int lengthBytes(B)
     andBool J0 <=Int lengthBytes(substrBytes(B, I, J))
  [simplification(44), preserves-definedness]
  rule pickFront(I, #bytes(B +Bytes _) _) => substrBytes(B, 0, I)
    requires I >Int 0 andBool I <=Int lengthBytes(B)    [simplification(45), preserves-definedness]
  rule pickFront(I, #bytes(B +Bytes BS) EF) => B +Bytes pickFront(I -Int lengthBytes(B), #bytes(BS) EF)
    requires I >Int lengthBytes(B)                      [simplification(45), preserves-definedness]

  rule dropFront(I, #bytes(B +Bytes BS) EF) => dropFront(0, #bytes(substrBytes(B, I, lengthBytes(B)) +Bytes BS) EF) 
    requires I >Int 0 andBool I <Int lengthBytes(B)     [simplification(45), preserves-definedness]
  rule dropFront(I, #bytes(B +Bytes BS) EF) => dropFront(I -Int lengthBytes(B), #bytes(BS) EF) 
    requires I >=Int lengthBytes(B)                     [simplification(45), preserves-definedness]
```

## writeBytes

If the write index is concrete, we can directly call `writeBytesBF` or `writeBytesEF`.

If the write index is symbolic, we use `#WB` to wrap the write operation. Unlike `writeBytes`, `#WB` contains a boolean value to determine whether the write operation has been completed. `true` means completed, `false` means not completed.

The `#WB` wrapper serves several purposes:

1. **Termination Control**: The boolean flag ensures that symbolic write operations eventually terminate by transitioning from `false` to `true` state, at which point concrete write functions can be applied when the index becomes concrete.

2. **Reordering for Optimization**: When multiple `#WB` operations are nested, the rules bring incomplete `#WB` operations (with `false` flag) to the terminal position, allowing them to traverse and find all possible merge opportunities. There is a special case when indices are the same but `NUM0 < NUM1`: in this situation, merging would introduce additional terms, so the operation is directly marked as completed to avoid complexity.

3. **Write Consolidation**: When multiple write operations target the same symbolic index with equal byte counts (`NUM0 == NUM1`), the rules merge them by eliminating the older write operation. When the new write has fewer bytes than the existing one (`NUM1 < NUM0`), the smaller write is also eliminated to maintain simplicity.

```k
  rule writeBytes(I, V, NUM, BF:SparseBytesBF) => writeBytesBF(I, V, NUM, BF) [simplification(45), concrete(I)]
  rule writeBytes(I, V, NUM, EF:SparseBytesEF) => writeBytesEF(I, V, NUM, EF) [simplification(45), concrete(I)]

  syntax SparseBytes ::= #WB(Bool, Int, Int, Int, SparseBytes) [function, total]
  rule #WB(_, I, V, NUM, B:SparseBytes) => writeBytes(I, V, NUM, B)     [concrete]
  rule writeBytes(I, V, NUM, B:SparseBytes) => #WB(false, I, V, NUM, B) [simplification]

  // Termination Control
  rule #WB(false, I, V, NUM, BF:SparseBytesBF) => #WB(true, I, V, NUM, BF)    [simplification]
  rule #WB(false, I, V, NUM, EF:SparseBytesEF) => #WB(true, I, V, NUM, EF)    [simplification]
  rule #WB(true,  I, V, NUM, BF:SparseBytesBF) => writeBytesBF(I, V, NUM, BF) [simplification, concrete(I)]
  rule #WB(true,  I, V, NUM, EF:SparseBytesEF) => writeBytesEF(I, V, NUM, EF) [simplification, concrete(I)]

  // Reordering for Optimization
  rule #WB(false, I0, V0, NUM0, #WB(true, I1, V1, NUM1, B:SparseBytes)) => #WB(true, I1, V1, NUM1, #WB(false, I0, V0, NUM0, B)) [simplification]
  rule #WB(false, I0, V0, NUM0, #WB(true, I1, V1, NUM1, B:SparseBytes)) => #WB(true, I0, V0, NUM0, #WB(true, I1, V1, NUM1, B)) 
    requires I0 ==Int I1 [simplification]

  // Write Consolidation
  rule #WB(false, I0, V0, NUM0, #WB(_, I1, _, NUM1, B:SparseBytes)) => #WB(false, I0, V0, NUM0, B) 
    requires NUM0 ==Int NUM1 andBool I0 ==Int I1 [simplification(45)]
  rule #WB(false, I0, V0, NUM0, #WB(_, I1, _, NUM1, B:SparseBytes)) => #WB(false, I0, V0, NUM0, B)
    requires NUM1 <Int NUM0 andBool I0 ==Int I1 [simplification(45)]  
```

## writeByteBF

To write a byte to a symbolic sparse byte region, we need to:

```k
  rule writeBytesBF(I, V, NUM, #bytes(B +Bytes BS) EF) => #bytes(replaceAtBytes(B, I, Int2Bytes(NUM, V, LE)) +Bytes BS) EF
    requires I >=Int 0 andBool I +Int NUM <=Int lengthBytes(B)  [simplification(45)]
  rule writeBytesBF(I, V, NUM, #bytes(B +Bytes BS) EF) => prepend(substrBytes(B, 0, I) +Bytes Int2Bytes(NUM, V, LE), dropFront(I +Int NUM -Int lengthBytes(B), #bytes(BS) EF))
    requires I <Int lengthBytes(B) andBool I +Int NUM >Int lengthBytes(B)    [simplification(45)]
  rule writeBytesBF(I, V, NUM, #bytes(B +Bytes BS) EF) => prepend(B, writeBytesBF(I -Int lengthBytes(B), V, NUM, #bytes(BS) EF))
    requires I >=Int lengthBytes(B)                             [simplification(45)]
```

```k
endmodule
```
