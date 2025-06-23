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
  syntax Bytes ::= pickFront(Int, SparseBytes) [function, total]
  rule pickFront(I, _) => .Bytes requires I <=Int 0
  rule pickFront(I, .SparseBytes) => .Bytes requires I >Int 0
  rule pickFront(I, #empty(N) _) => padRightBytes(.Bytes, I, 0)
    requires I >Int 0 andBool I <=Int N
  rule pickFront(I, #empty(N) BF) => padRightBytes(.Bytes, I, 0) +Bytes pickFront(I -Int N, BF)
    requires I >Int 0 andBool I >Int N
  rule pickFront(I, #bytes(B) _) => substrBytes(B, 0, I)
    requires I >Int 0 andBool I <=Int lengthBytes(B)
  rule pickFront(I, #bytes(B) EF) => B +Bytes pickFront(I -Int lengthBytes(B), EF)
    requires I >Int lengthBytes(B)
```
`dropFront` is a helper function for dropping the first `N` bytes from a `SparseBytes` value.
```k
  syntax SparseBytes ::=  dropFront(Int, SparseBytes) [function, total]
  rule dropFront(I, SBS) => SBS    requires I <=Int 0
  rule dropFront(I, .SparseBytes) => .SparseBytes requires I >Int 0
  rule dropFront(I, #empty(N) BF) => #empty(N -Int I) BF requires I >Int 0 andBool I <Int N
  rule dropFront(I, #empty(N) BF) => dropFront(I -Int N, BF) requires I >Int 0 andBool I >=Int N
  rule dropFront(I, #bytes(B) EF) => dropFront(0, #bytes(substrBytes(B, I, lengthBytes(B))) EF) 
    requires I >Int 0 andBool I <Int lengthBytes(B)
  rule dropFront(I, #bytes(B) EF) => dropFront(I -Int lengthBytes(B), EF) requires I >=Int lengthBytes(B)
```
`readBytes(SBS, I, NUM)` reads `NUM` bytes from a given index `I` in `O(E)` time, where `E` is the number of `#empty(_)` or `#bytes(_)` entries in the list up to the location of the index.
```k
  syntax Int ::= readBytes(Int, Int, SparseBytes) [function, total]

  rule readBytes(I, NUM, SBS) => Bytes2Int(pickFront(NUM, dropFront(I, SBS)), LE, Unsigned)
```
`writeBytes(SBS, I, V, NUM)` writes value `V` with length `NUM` bytes to a given index `I`. With regards to time complexity,
- If the index is in the middle of an existing `#empty(_)` or `#bytes(_)` region, time complexity is `O(E)` where `E` is the number of entries up to the index.
- If the index happens to be the first or last index in an `#empty(_)` region directly boarding a `#bytes(_)` region, then the `#bytes(_)` region must be re-allocated to append the new value, giving worst-case `O(E + B)` time, where `E` is the number of entries up to the location of the index and `B` is the size of this existing `#bytes(_)`.
```k
  syntax SparseBytes ::=
      writeBytes  (Int, Int, Int, SparseBytes  ) [function, total]
    | writeBytesEF(Int, Int, Int, SparseBytesEF) [function, total]
    | writeBytesBF(Int, Int, Int, SparseBytesBF) [function, total]

  rule writeBytes(I, V, NUM, BF:SparseBytesBF) => writeBytesBF(I, V, NUM, BF)
  rule writeBytes(I, V, NUM, EF:SparseBytesEF) => writeBytesEF(I, V, NUM, EF)

  rule writeBytesEF(I, _, _  , _           ) => .SparseBytes    requires I <Int 0 // error case for totality
  rule writeBytesEF(I, V, NUM, .SparseBytes) => prependEmpty(I, #bytes(Int2Bytes(NUM, V, LE)) .SparseBytes)    requires I >=Int 0
  rule writeBytesEF(I, V, NUM, #empty(N) BF) => prependEmpty(I, prepend(Int2Bytes(NUM, V, LE), prependEmpty(N -Int I -Int NUM, BF)))
    requires I >=Int 0 andBool I +Int NUM <=Int N
  rule writeBytesEF(I, V, NUM, #empty(N) BF) => prependEmpty(I, prepend(Int2Bytes(NUM, V, LE), dropFront(I +Int NUM -Int N, BF)))
    requires I <Int N andBool I +Int NUM >Int N
  rule writeBytesEF(I, V, NUM, #empty(N) BF) => prependEmpty(N, writeBytesBF(I -Int N, V, NUM, BF))
    requires I >=Int N

  rule writeBytesBF(I, _, _  , _           ) => .SparseBytes    requires I <Int 0 // error case for totality
  rule writeBytesBF(I, V, NUM, #bytes(B) EF) => #bytes(replaceAtBytes(B, I, Int2Bytes(NUM, V, LE))) EF
    requires I >=Int 0 andBool I +Int NUM <=Int lengthBytes(B)
  rule writeBytesBF(I, V, NUM, #bytes(B) EF) => prepend(substrBytes(B, 0, I) +Bytes Int2Bytes(NUM, V, LE), dropFront(I +Int NUM -Int lengthBytes(B), EF))
    requires I <Int lengthBytes(B) andBool I +Int NUM >Int lengthBytes(B)
  rule writeBytesBF(I, V, NUM, #bytes(B) EF) => prepend(B, writeBytesEF(I -Int lengthBytes(B), V, NUM, EF))
    requires I >=Int lengthBytes(B)
endmodule
```
