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
  rule prependEmpty(I, _               ) => .SparseBytes        requires I <Int 0 // error case for totality
  rule prependEmpty(I, SBS             ) => SBS                 requires I ==Int 0
  rule prependEmpty(I, .SparseBytes    ) => .SparseBytes        requires I >Int 0
  rule prependEmpty(I, #empty(N) BF    ) => #empty(I +Int N) BF requires I >Int 0
  rule prependEmpty(I, BF:SparseBytesBF) => #empty(I) BF        requires I >Int 0
```
`pickFront` is a helper function for picking the first `N` bytes from a `SparseBytes` value.
```k
  syntax Bytes ::= pickFront(SparseBytes, Int) [function, total]
  rule pickFront(_, I) => .Bytes requires I <=Int 0
  rule pickFront(.SparseBytes, I) => .Bytes requires I >Int 0
  rule pickFront(#empty(N) _, I) => padRightBytes(.Bytes, I, 0)
    requires I >Int 0 andBool I <=Int N
  rule pickFront(#empty(N) BF, I) => padRightBytes(.Bytes, I, 0) +Bytes pickFront(BF, I -Int N)
    requires I >Int 0 andBool I >Int N
  rule pickFront(#bytes(B) _, I) => substrBytes(B, 0, I)
    requires I >Int 0 andBool I <=Int lengthBytes(B)
  rule pickFront(#bytes(B) EF, I) => B +Bytes pickFront(EF, I -Int lengthBytes(B))
    requires I >Int lengthBytes(B)
```
`dropFront` is a helper function for dropping the first `N` bytes from a `SparseBytes` value.
```k
  syntax SparseBytes ::=  dropFront(SparseBytes, Int) [function, total]
  rule dropFront(SBS, I) => SBS    requires I <=Int 0
  rule dropFront(.SparseBytes, I) => .SparseBytes requires I >Int 0
  rule dropFront(#empty(N) BF, I) => #empty(N -Int I) BF requires I >Int 0 andBool I <Int N
  rule dropFront(#empty(N) BF, I) => dropFront(BF, I -Int N) requires I >Int 0 andBool I >=Int N
  rule dropFront(#bytes(B) EF, I) => dropFront(#bytes(substrBytes(B, I, lengthBytes(B))) EF, 0) 
    requires I >Int 0 andBool I <Int lengthBytes(B)
  rule dropFront(#bytes(B) EF, I) => dropFront(EF, I -Int lengthBytes(B)) requires I >=Int lengthBytes(B)
```
`readBytes(SBS, I, NUM)` reads `NUM` bytes from a given index `I` in `O(E)` time, where `E` is the number of `#empty(_)` or `#bytes(_)` entries in the list up to the location of the index.
```k
  syntax Int ::= readBytes(SparseBytes, Int, Int) [function, total]

  rule readBytes(SBS, I, NUM) => Bytes2Int(pickFront(dropFront(SBS, I), NUM), LE, Unsigned)
```
`writeBytes(SBS, I, V, NUM)` writes value `V` with length `NUM` bytes to a given index `I`. With regards to time complexity,
- If the index is in the middle of an existing `#empty(_)` or `#bytes(_)` region, time complexity is `O(E)` where `E` is the number of entries up to the index.
- If the index happens to be the first or last index in an `#empty(_)` region directly boarding a `#bytes(_)` region, then the `#bytes(_)` region must be re-allocated to append the new value, giving worst-case `O(E + B)` time, where `E` is the number of entries up to the location of the index and `B` is the size of this existing `#bytes(_)`.
```k
  syntax SparseBytes ::=
      writeBytes  (SparseBytes  , Int, Int, Int) [function, total]
    | writeBytesEF(SparseBytesEF, Int, Int, Int) [function, total]
    | writeBytesBF(SparseBytesBF, Int, Int, Int) [function, total]

  rule writeBytes(BF:SparseBytesBF, I, V, NUM) => writeBytesBF(BF, I, V, NUM)
  rule writeBytes(EF:SparseBytesEF, I, V, NUM) => writeBytesEF(EF, I, V, NUM)

  rule writeBytesEF(_           , I, _, _) => .SparseBytes    requires I <Int 0 // error case for totality
  rule writeBytesEF(.SparseBytes, I, V, NUM) => prependEmpty(I, #bytes(Int2Bytes(NUM, V, LE)) .SparseBytes)    requires I >=Int 0
  rule writeBytesEF(#empty(N) BF, I, V, NUM) => prependEmpty(I, prepend(Int2Bytes(NUM, V, LE), prependEmpty(N -Int I -Int NUM, BF)))
    requires I >=Int 0 andBool I +Int NUM <=Int N
  rule writeBytesEF(#empty(N) BF, I, V, NUM) => prependEmpty(I, prepend(Int2Bytes(NUM, V, LE), dropFront(BF, I +Int NUM -Int N)))
    requires I <Int N andBool I +Int NUM >Int N
  rule writeBytesEF(#empty(N) BF, I, V, NUM) => prependEmpty(N, writeBytesBF(BF, I -Int N, V, NUM))
    requires I >=Int N

  rule writeBytesBF(_           , I, _, _  ) => .SparseBytes    requires I <Int 0 // error case for totality
  rule writeBytesBF(#bytes(B) EF, I, V, NUM) => #bytes(replaceAtBytes(B, I, Int2Bytes(NUM, V, LE))) EF
    requires I >=Int 0 andBool I +Int NUM <=Int lengthBytes(B)
  rule writeBytesBF(#bytes(B) EF, I, V, NUM) => prepend(substrBytes(B, 0, I) +Bytes Int2Bytes(NUM, V, LE), dropFront(EF, I +Int NUM -Int lengthBytes(B)))
    requires I <Int lengthBytes(B) andBool I +Int NUM >Int lengthBytes(B)
  rule writeBytesBF(#bytes(B) EF, I, V, NUM) => prepend(B, writeBytesEF(EF, I -Int lengthBytes(B), V, NUM))
    requires I >=Int lengthBytes(B)
endmodule
```
