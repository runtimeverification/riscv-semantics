# `XLEN`-bit Word Datatype
In this file, we define a `Word` datatype representing a sequence of `XLEN` bits, where `XLEN=32` for `RV32*` ISAs and `XLEN=64` for `RV64*` ISAs.
```k
module WORD
  imports BOOL
  imports BYTES
  imports INT

  syntax Int ::= "XLEN" [macro]
  rule XLEN => 32
```
In our semantics, we represent bit sequences using K's `Int` type, which supports arbitrary precision and infinite sign extension in two's complement format. The `Word` type is essentially an unsigned integer wrapper around `Int`, where only the `XLEN` least significant bits contain meaningful data and all higher bits are set to zero.

A `Word` can be interpreted as an `XLEN`-bit signed two's complement integer by infinitely sign extending.
```k
  syntax Int ::= Word2SInt(Int) [function, total]
  rule Word2SInt(I) => infSignExtend(I, XLEN)

  syntax Int ::= infSignExtend(bits: Int, signBitIdx: Int) [function, total]
  rule infSignExtend(B, L) => (-1 <<Int L) |Int B requires (B >>Int (L -Int 1)) &Int 1 ==Int 1
  rule infSignExtend(B, _) => B [owise]
```
`N`-bit signed two's complement integers with `N <= XLEN` can also be sign extended to `XLEN`-bits.
```k
  syntax Int ::= signExtend(bits: Int, signBitIdx: Int) [function, total]
  rule signExtend(B, L) => ((2 ^Int (XLEN -Int L) -Int 1) <<Int L) |Int B requires (B >>Int (L -Int 1)) &Int 1 ==Int 1
  rule signExtend(B, _) => B [owise]
```
Booleans can be encoded as `Word`s in the obvious way
```k
  syntax Int ::= Bool2Word(Bool) [function, total]
  rule Bool2Word(false) => 0
  rule Bool2Word(true ) => 1
```
The rest of this file defines various numeric and bitwise operations over `Word`. Most of these are straightforward operations on the underlying `Int`.
```k
  syntax Bool ::= Int "==Word" Int [function, total]
  rule W1 ==Word W2 => W1 ==Int W2

  syntax Bool ::= Int "=/=Word" Int [function, total]
  rule W1 =/=Word W2 => W1 =/=Int W2
```
The `s` prefix denotes a signed operation while `u` denotes an unsigned operation.
```k
  syntax Bool ::= Int "<sWord" Int [function, total]
  rule W1 <sWord W2 => Word2SInt(W1) <Int Word2SInt(W2)

  syntax Bool ::= Int ">=sWord" Int [function, total]
  rule W1 >=sWord W2 => Word2SInt(W1) >=Int Word2SInt(W2)

  syntax Bool ::= Int "<uWord" Int [function, total]
  rule W1 <uWord W2 => W1 <Int W2

  syntax Bool ::= Int ">=uWord" Int [function, total]
  rule W1 >=uWord W2 => W1 >=Int W2
```
To avoid syntax conflicts, we define the following syntax with `left` associativity and clear precedence over the bitwise operations.
```k
  syntax Int ::= left:
                  Int "*Word"    Int [function, total, symbol(mulWord)]
                | Int "*hWord"   Int [function, total, symbol(mulhWord)]
                | Int "*huWord"  Int [function, total, symbol(mulhuWord)]
                | Int "*hsuWord" Int [function, total, symbol(mulhsuWord)]
                > left:
                  Int "+Word"    Int [function, total, symbol(addWord)]
                | Int "-Word"    Int [function, total, symbol(subWord)]
                > left:
                  Int ">>lWord"  Int [function, total, symbol(rshWord)]
                | Int ">>aWord"  Int [function, total, symbol(ashWord)]
                | Int "<<Word"   Int [function, total, symbol(lshWord)]
                > left:
                  Int "&Word"    Int [function, total, symbol(andWord)]
                > left:
                  Int "xorWord"  Int [function, total, symbol(xorWord)]
                > left:
                  Int "|Word"    Int [function, total, symbol(orWord)]
```

Note that two's complement enables us to use a single addition or subtraction operation for both signed and unsigned values.
```k
  rule W1 +Word W2 => chop(W1 +Int W2)
  rule W1 -Word W2 => chop(W1 -Int W2)
```
The same is true for the `XLEN` least-significant bits of the result of multiplication.
```k
  rule W1 *Word W2 => chop(W1 *Int W2)
```
The value of the upper `XLEN` bits however depends on signedness of the operands, as reflected by the following functions.
```k
  rule W1 *hWord W2 => chop((Word2SInt(W1) *Int Word2SInt(W2)) >>Int XLEN)
  rule W1 *huWord W2 => chop((W1 *Int W2) >>Int XLEN)
  rule W1 *hsuWord W2 => chop((Word2SInt(W1) *Int W2) >>Int XLEN)
```
Above, the `chop` utility function
```k
  syntax Int ::= chop(Int) [function, total]
  rule chop(I) => I &Int (2 ^Int XLEN -Int 1)
```
is used to zero-out all but the least-significant `XLEN`-bits in case of overflow.
```k
  rule W1 &Word W2 => W1 &Int W2

  rule W1 |Word W2 => W1 |Int W2

  rule W1 xorWord W2 => W1 xorInt W2

  rule W1 <<Word W2 => chop(W1 <<Int W2) requires 0 <=Int W2
  rule _     <<Word W2 => 0              requires W2 <Int 0
```
For right shifts, we provide both arithmetic and logical variants.

The logical right shift (`>>lWord`) is implemented using the arithmetic right shift operator `>>Int` because:
1. `Int` values are infinitely sign-extended two's complement integers
2. `>>Int` arithmetically shifts by padding with the infinitely repeated sign bit
3. For a word, only the least-significant `XLEN`-bits are populated, so the infinitely repeated sign bit is always `0`

Therefore, applying `>>Int` to a `Word` value will always pad with `0`s, correctly implementing a logical right shift.
```k
  rule W1 >>lWord W2 => W1 >>Int W2 requires 0 <=Int W2
  rule _  >>lWord W2 => 0           requires W2 <Int 0
```
For arithmetic right shift (`>>aWord`), we first convert to an infinitely sign-extended `Int` using `Word2SInt`, ensuring `>>Int` will pad with `1`s for a negative `Word`. The result is then chopped back to a `Word`.
```k
  rule W1 >>aWord W2 => chop(Word2SInt(W1) >>Int W2) requires 0 <=Int W2
  rule _  >>aWord W2 => 0                         requires W2 <Int 0
endmodule
```
