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
Throughout the semantics, we use K's arbitrary-precision, infinitely sign-extended, two's-complement integer type `Int` to store arbitrary bit sequences. A `Word` consists of a single `Int`, with the `XLEN` least-signficant bits storing the desired bit sequence and all other bits zeroed.
```k
  syntax Word ::= W(Int) [symbol(W)]
```
A `Word` can be interpreted as an unsigned integer by directly returning the underlying `Int`,
```k
  syntax Int ::= Word2UInt(Word) [function, total]
  rule Word2UInt(W(I)) => I
```
or interpreted as an `XLEN`-bit signed two's complement integer by infinitely sign extending.
```k
  syntax Int ::= Word2SInt(Word) [function, total]
  rule Word2SInt(W(I)) => infSignExtend(I, XLEN)

  syntax Int ::= infSignExtend(bits: Int, signBitIdx: Int) [function, total]
  rule infSignExtend(B, L) => (-1 <<Int L) |Int B requires (B >>Int (L -Int 1)) &Int 1 ==Int 1
  rule infSignExtend(B, _) => B [owise]
```
`N`-bit signed two's complement integers with `N <= XLEN` can also be sign extended to `XLEN`-bits.
```k
  syntax Word ::= signExtend(bits: Int, signBitIdx: Int) [function, total]
  rule signExtend(B, L) => W(((2 ^Int (XLEN -Int L) -Int 1) <<Int L) |Int B) requires (B >>Int (L -Int 1)) &Int 1 ==Int 1
  rule signExtend(B, _) => W(B) [owise]
```
Booleans can be encoded as `Word`s in the obvious way
```k
  syntax Word ::= Bool2Word(Bool) [function, total]
  rule Bool2Word(false) => W(0)
  rule Bool2Word(true ) => W(1)
```
The rest of this file defines various numeric and bitwise operations over `Word`. Most of these are straightforwad operations on the underlying `Int`.
```k
  syntax Bool ::= Word "==Word" Word [function, total]
  rule W(I1) ==Word W(I2) => I1 ==Int I2

  syntax Bool ::= Word "=/=Word" Word [function, total]
  rule W(I1) =/=Word W(I2) => I1 =/=Int I2
```
The `s` prefix denotes a signed operation while `u` denotes an unsigned operation.
```k
  syntax Bool ::= Word "<sWord" Word [function, total]
  rule W1 <sWord W2 => Word2SInt(W1) <Int Word2SInt(W2)

  syntax Bool ::= Word ">=sWord" Word [function, total]
  rule W1 >=sWord W2 => Word2SInt(W1) >=Int Word2SInt(W2)

  syntax Bool ::= Word "<uWord" Word [function, total]
  rule W(I1) <uWord W(I2) => I1 <Int I2

  syntax Bool ::= Word ">=uWord" Word [function, total]
  rule W(I1) >=uWord W(I2) => I1 >=Int I2
```
Note that two's complement enables us to use a single addition or subtraction operation for both signed and unsigned values.
```k
  syntax Word ::= Word "+Word" Word [function, total]
  rule W(I1) +Word W(I2) => chop(I1 +Int I2)

  syntax Word ::= Word "-Word" Word [function, total]
  rule W(I1) -Word W(I2) => chop(I1 -Int I2)
```
The same is true for the `XLEN` least-significant bits of the result of multiplication.
```k
  syntax Word ::= Word "*Word" Word [function, total, symbol(mulWord)]
  rule W(I1) *Word W(I2) => chop(I1 *Int I2)
```
The value of the upper `XLEN` bits however depends on signedness of the operands, as reflected by the followig functions.
```k
  syntax Word ::= Word "*hWord" Word [function, total, symbol(mulhWord)]
  rule W1 *hWord W2 => chop((Word2SInt(W1) *Int Word2SInt(W2)) >>Int XLEN)

  syntax Word ::= Word "*huWord" Word [function, total, symbol(mulhuWord)]
  rule W(I1) *huWord W(I2) => chop((I1 *Int I2) >>Int XLEN)

  syntax Word ::= Word "*hsuWord" Word [function, total, symbol(mulhsuWord)]
  rule W1 *hsuWord W(I2) => chop((Word2SInt(W1) *Int I2) >>Int XLEN)
```
Above, the `chop` utility function
```k
  syntax Word ::= chop(Int) [function, total]
  rule chop(I) => W(I &Int (2 ^Int XLEN -Int 1))
```
is used to zero-out all but the least-significant `XLEN`-bits in case of overflow.
```k
  syntax Word ::= Word "&Word" Word [function, total]
  rule W(I1) &Word W(I2) => W(I1 &Int I2)

  syntax Word ::= Word "|Word" Word [function, total]
  rule W(I1) |Word W(I2) => W(I1 |Int I2)

  syntax Word ::= Word "xorWord" Word [function, total]
  rule W(I1) xorWord W(I2) => W(I1 xorInt I2)

  syntax Word ::= Word "<<Word" Int [function, total]
  rule W(I1) <<Word I2 => chop(I1 <<Int I2) requires 0 <=Int I2
  rule _     <<Word I2 => W(0)              requires I2 <Int 0
```
For right shifts, we provide both arithmetic and logical variants.

Counterintuitively, we use the arithmetic right shift operator `>>Int` for `Int` to implement the logical right shift operator `>>lWord` for `Word`. Indeed, note the following:
- `Int` values are infinitely sign-extended two's complement integers.
- `>>Int` arithmetically shifts by padding with the infinitely repeated sign bit.
- For an `I:Int` underlying `W(I):Word`, only the least-significant `XLEN`-bits of `I` are populated, so the infinitely repeated sign bit is always `0`.

That is, for any `I:Int` underlying some `W(I):Word`, applying `>>Int` will always pad with `0`s, correctly implementing a logical right shift.
```k
  syntax Word ::= Word ">>lWord" Int [function, total]
  rule W(I1) >>lWord I2 => W(I1 >>Int I2) requires 0 <=Int I2
  rule _     >>lWord I2 => W(0)           requires I2 <Int 0
```
To actually perform an arithmetic shift over `Word`, we first convert to an infinitely sign-extended `Int` of equal value using `Word2SInt`, ensuring `>>Int` will pad with `1`s for a negative `Word`. The final result will still be infinitely sign-extended, so we must `chop` it back to a `Word`.
```k
  syntax Word ::= Word ">>aWord" Int [function, total]
  rule W1 >>aWord I2 => chop(Word2SInt(W1) >>Int I2) requires 0 <=Int I2
  rule _  >>aWord I2 => W(0)                         requires I2 <Int 0
endmodule
```
