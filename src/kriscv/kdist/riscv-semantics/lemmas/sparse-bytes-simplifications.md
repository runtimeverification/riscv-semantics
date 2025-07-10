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

Simplification rules for pickFront and dropFront operations on symbolic write blocks (#WB)
- Default case: For most symbolic write operations, we can bypass the #WB wrapper and apply pickFront directly to the underlying byte structure
```k
  rule pickFront(PICK, #WB(_, I, _, _, B:SparseBytes)) => pickFront(PICK, B) 
    requires PICK <=Int I
    [simplification(45)]
```
- Special case for zero-indexed writes: When a write starts at position 0, we must combine bytes from both the written value and the remaining underlying structure
```k
  rule pickFront(PICK, #WB(_, I, V, NUM, B:SparseBytes)) => Int2Bytes(minInt(PICK, NUM), V, LE) +Bytes pickFront(maxInt(0, PICK -Int NUM), B >>SparseBytes minInt(PICK, NUM))
    requires 0 ==Int I [simplification(40)]
```
- Front-dropping with symbolic writes: Adjust both the write offset and apply dropFront to the underlying structure to maintain correct relative positioning
```k
  rule dropFront(DROP, #WB(FLAG, I, V, NUM, B:SparseBytes)) => #WB(FLAG, I -Int DROP, V, NUM, dropFront(DROP, B)) 
    [simplification(45)]
```

## Right Shift Operations

The `>>SparseBytes` operator performs a right shift operation on SparseBytes, effectively dropping the first N bytes from the sparse byte structure while maintaining the integer value semantics of the remaining bytes. Unlike `dropFront`, which simply removes N bytes from the beginning, `>>SparseBytes` performs a byte-level right shift that preserves the underlying integer representation of the data.

This is primarily used in `pickFront` operations when we need to extract bytes from a specific offset within the sparse byte structure.

```k
  syntax SparseBytes ::= SparseBytes ">>SparseBytes" Int  [function, total]

  // For concrete sparse bytes, we can directly use dropFront to simplify the operation
  rule SBS >>SparseBytes SHIFT => dropFront(SHIFT, SBS) [concrete]
  
  // Symbolic write case: Adjust the written value by right-shifting and recursively apply to underlying structure
  rule #WB(FLAG, I, V, NUM, B:SparseBytes) >>SparseBytes SHIFT => #WB(FLAG, maxInt(0, I -Int SHIFT), V >>Int (SHIFT *Int 8), NUM, B >>SparseBytes SHIFT)
    requires SHIFT >=Int 0 [simplification(45), preserves-definedness]
```

## writeBytes

If the write index is concrete, we can directly call `writeBytesBF` or `writeBytesEF`.

```k
  rule writeBytes(I, V, NUM, BF:SparseBytesBF) => writeBytesBF(I, V, NUM, BF) [simplification(45), concrete(I)]
  rule writeBytes(I, V, NUM, EF:SparseBytesEF) => writeBytesEF(I, V, NUM, EF) [simplification(45), concrete(I)]
```

If the write index is symbolic, we use `#WB` to wrap the write operation. Unlike `writeBytes`, `#WB` contains a boolean value to determine whether the write operation has been completed. `true` means completed, `false` means not completed.

```k
  syntax SparseBytes ::= #WB(Bool, Int, Int, Int, SparseBytes) [function, total]
  rule #WB(_, I, V, NUM, B:SparseBytes) => writeBytes(I, V, NUM, B)     [concrete]
  rule writeBytes(I, V, NUM, B:SparseBytes) => #WB(false, I, V, NUM, B) [simplification]
```

**Termination Control**: The boolean flag ensures that symbolic write operations eventually terminate by transitioning from `false` to `true` state, at which point concrete write functions can be applied when the index becomes concrete.

```k
  rule #WB(_, I, _, NUM, B:SparseBytes) => B requires I <Int 0 orBool NUM <=Int 0 [simplification(40)]
  rule #WB(false, I, V, NUM, BF:SparseBytesBF) => #WB(true, I, V, NUM, BF)        [simplification]
  rule #WB(false, I, V, NUM, EF:SparseBytesEF) => #WB(true, I, V, NUM, EF)        [simplification]
  rule #WB(true,  I, V, NUM, BF:SparseBytesBF) => writeBytesBF(I, V, NUM, BF)     [simplification, concrete(I)]
  rule #WB(true,  I, V, NUM, EF:SparseBytesEF) => writeBytesEF(I, V, NUM, EF)     [simplification, concrete(I)]
```

**Reordering for Optimization**: When multiple `#WB` operations are nested, the rules bring incomplete `#WB` operations (with `false` flag) to the terminal position, allowing them to traverse and find all possible merge opportunities. 

```k
  rule #WB(false, I0, V0, NUM0, #WB(true, I1, V1, NUM1, B:SparseBytes)) => #WB(true, I1, V1, NUM1, #WB(false, I0, V0, NUM0, B)) 
    requires I0 +Int NUM0 <=Int I1 orBool I1 +Int NUM1 <=Int I0 [simplification]
```

The rule below handles a termination edge case: it immediately marks the operation as complete with reduced priority to avoid infinite rewriting cycles.

```k
  rule #WB(false, I0, V0, NUM0, #WB(true, I1, V1, NUM1, B:SparseBytes)) => #WB(true, I0, V0, NUM0, #WB(true, I1, V1, NUM1, B)) [simplification(60)]
```

**Write Consolidation**: When multiple write operations target the same symbolic index with equal byte counts (`NUM0 == NUM1`), the rules merge them by eliminating the older write operation. When the new write has fewer bytes than the existing one (`NUM1 < NUM0`), the smaller write is also eliminated to maintain simplicity.

```k
  rule #WB(false, I0, V0, NUM0, #WB(_, I1, _, NUM1, B:SparseBytes)) => #WB(false, I0, V0, NUM0, B)
    requires I0 <=Int I1 andBool I1 +Int NUM1 <=Int I0 +Int NUM0  [simplification(45)]  
```

## writeBytesBF

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
