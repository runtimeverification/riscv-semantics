# Sparse Bytes Datatype
In this file, we define a `SparseBytes` datatype representing a byte array with large segments of uninitialized data, optimized for space efficiency.
```k
module SPARSE-BYTES
  imports BOOL
  imports BYTES
  imports INT
```
Concretely, a `SparseBytes` value is a list of items
```k
  syntax BytesSBItem ::= #bytes(Bytes) [symbol(SparseBytes:#bytes)]
  syntax EmptySBItem ::= #empty(Int)   [symbol(SparseBytes:#empty)]
```
where `#bytes(B)` represents a contiguous segment of initialized data `B:Bytes` and `#empty(N)` represents a contiguous segment of uninitialized data `N` bytes wide.

We define `SparseBytes` in terms of two mutually recursive sorts:
-`SparseBytesEF`, representing a `SparseBytes` value which is either completely empty (`.SparseBytes`) or begins with an `#empty(_)` entry
-`SparseBytesBF`, representing a `SparseBytes` value which begins with a `#bytes(_)` entry

Structuring `SparseBytes` in this way forces entries to always alternate between `#empty(_)` and `#bytes(_)`, i.e., ensuring contiguous uninitialized regions are packed together and contiguous initialized regions are packed together. As a result, many functions over `SparseBytes` are naturally implemented as mutually recursive functions over `SparseBytesEF` and `SparseBytesBF`.
```k
  syntax SparseBytes ::=
      SparseBytesEF
    | SparseBytesBF

  // SparseBytes with a leading EmptySBItem (EF = Empty First)
  syntax SparseBytesEF ::=
      ".SparseBytes"            [symbol(.SparseBytes)]
    | EmptySBItem SparseBytesBF [symbol(SparseBytes:EmptyCons)]

  // SparseBytes with a leading BytesSBItem (BF = Bytes First)
  syntax SparseBytesBF ::=
      BytesSBItem SparseBytesEF [symbol(SparseBytes:BytesCons)]
```
We provide helpers to prepend either data or an empty region to an existing `SparseBytes`. Note that `prepend` has worst-case time complexity `O(B + BS)` where `B` is the length of the prepended data and `BS` is the length of initialized data at the start of the list.
```k
  syntax SparseBytesBF ::= prepend(Bytes, SparseBytes) [function, total]
  rule prepend(B, EF:SparseBytesEF) => #bytes(B) EF
  rule prepend(B, #bytes(BS) EF   ) => #bytes(B +Bytes BS) EF
```
`prependEmpty` has `O(1)` time complexity.
```k
  syntax SparseBytes ::= prependEmpty(Int, SparseBytes) [function, total]
  rule prependEmpty(I, _               ) => .SparseBytes        requires I <Int 0 // dummy value for invalid argument to keep totality
  rule prependEmpty(I, SBS             ) => SBS                 requires I ==Int 0
  rule prependEmpty(I, .SparseBytes    ) => .SparseBytes        requires I >Int 0
  rule prependEmpty(I, #empty(N) BF    ) => #empty(I +Int N) BF requires I >Int 0
  rule prependEmpty(I, BF:SparseBytesBF) => #empty(I) BF        requires I >Int 0
```
`readByte` reads a single byte from a given index in `O(E)` time, where `E` is the number of `#empty(_)` or `#bytes(_)` entries in the list up to the location of the index. The result is either
- an `Int` in the range `[0, 255)` giving the byte value at the index, or
- `.Byte` if the index does not point to initialized data
```k
  syntax MaybeByte ::=
      Int
    | ".Byte"

  syntax MaybeByte ::=
      readByte  (SparseBytes  , Int) [function, total]
    | readByteEF(SparseBytesEF, Int) [function, total]
    | readByteBF(SparseBytesBF, Int) [function, total]

  rule readByte(EF:SparseBytesEF, I) => readByteEF(EF, I)
  rule readByte(BF:SparseBytesBF, I) => readByteBF(BF, I)

  rule readByteEF(.SparseBytes, _) => .Byte
  rule readByteEF(#empty(N) _ , I) => .Byte                    requires I <Int N
  rule readByteEF(#empty(N) BF, I) => readByteBF(BF, I -Int N) requires I >=Int N

  rule readByteBF(#bytes(_) _ , I) => .Byte  requires I <Int 0
  rule readByteBF(#bytes(B) _ , I) => B[ I ] requires I >=Int 0 andBool I <Int lengthBytes(B)
  rule readByteBF(#bytes(B) EF, I) => readByteEF(EF, I -Int lengthBytes(B))
                                             requires I >=Int lengthBytes(B)
```
`writeByte` writes a single byte to a given index. With regards to time complexity,
- If the index is in the middle of an existing `#empty(_)` or `#bytes(_)` region, time complexity is `O(E)` where `E` is the number of entries up to the index.
- If the index happens to be the first or last index in an `#empty(_)` region directly boarding a `#bytes(_)` region, then the `#bytes(_)` region must be re-allocated to append the new value, giving worst-case `O(E + B)` time, where `E` is the number of entries up to the location of the index and `B` is the size of this existing `#bytes(_)`.
```k
  syntax SparseBytes ::=
      writeByte  (SparseBytes  , Int, Int) [function, total]
    | writeByteEF(SparseBytesEF, Int, Int) [function, total]
    | writeByteBF(SparseBytesBF, Int, Int) [function, total]

  rule writeByte(BF:SparseBytesBF, I, V) => writeByteBF(BF, I, V)
  rule writeByte(EF:SparseBytesEF, I, V) => writeByteEF(EF, I, V)

  rule writeByteEF(_           , I, _) => .SparseBytes                                       requires I <Int 0
  rule writeByteEF(.SparseBytes, I, V) => #bytes(Int2Bytes(1, V, BE)) .SparseBytes           requires I ==Int 0
  rule writeByteEF(.SparseBytes, I, V) => #empty(I) #bytes(Int2Bytes(1, V, BE)) .SparseBytes requires I >Int 0
  rule writeByteEF(#empty(N) BF, I, V) => prependEmpty(I, prepend(Int2Bytes(1, V, BE), prependEmpty((N -Int I) -Int 1, BF)))
                                                                                             requires I >=Int 0 andBool I <Int N
  rule writeByteEF(#empty(N) BF, I, V) => prependEmpty(N, writeByteBF(BF, I -Int N, V))      requires I >=Int N

  rule writeByteBF(_           , I, _) => .SparseBytes           requires I <Int 0
  rule writeByteBF(#bytes(B) EF, I, V) => #bytes(B[ I <- V ]) EF requires I >=Int 0 andBool I <Int lengthBytes(B)
  rule writeByteBF(#bytes(B) EF, I, V) => prepend(B, writeByteEF(EF, I -Int lengthBytes(B), V))
                                                                 requires I >=Int lengthBytes(B)
endmodule
```
