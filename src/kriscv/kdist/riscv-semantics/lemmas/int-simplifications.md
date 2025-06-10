# Int Simplifications

```k
module INT-SIMPLIFICATIONS [symbolic]
  imports INT
  imports BYTES
  imports K-EQUAL
  imports BOOL
  imports INT-SIMPLIFICATION-HASKELL
```

## Shift Lemmas

```k
  rule [int-lsh-lsh]: (W0 <<Int N0) <<Int N1 => W0 <<Int (N0 +Int N1)
    requires 0 <=Int N0 andBool 0 <=Int N1
    [simplification, preserves-definedness]
  rule [int-lsh-less-than-32bits]: (X <<Int Y) <Int 4294967296 => true
    requires 0 <=Int X andBool 0 <=Int Y andBool Y <Int 32 andBool X <Int 2 ^Int (32 -Int Y)
    [simplification, preserves-definedness]
  rule [int-lsh-non-negative]: 0 <=Int (X <<Int Y) => true
    requires 0 <=Int X andBool 0 <=Int Y [simplification]
```

## &Int Lemmas

```k
  rule [chop-32bits]: X &Int 4294967295 => X requires 0 <=Int X andBool X <Int 4294967296 [simplification]
  rule [int-and-assoc]: (X &Int Y) &Int Z => X &Int (Y &Int Z) [simplification, symbolic(X), concrete(Y,Z)]
  rule [int-and-add-assoc-8]: ((X &Int 255) +Int Y) &Int 255 => (X +Int Y) &Int 255
    requires 0 <=Int X andBool 0 <=Int Y
    [simplification]
  rule [int-and-add-assoc-16]: ((X &Int 65535) +Int Y) &Int 65535 => (X +Int Y) &Int 65535
    requires 0 <=Int X andBool 0 <=Int Y
    [simplification]
  rule [int-and-add-assoc-32]: ((X &Int 4294967295) +Int Y) &Int 4294967295 => (X +Int Y) &Int 4294967295
    requires 0 <=Int X andBool 0 <=Int Y
    [simplification]
```

## Inequality Lemmas

```k
  rule [int-and-ineq]: 0 <=Int A &Int B => true requires 0 <=Int A andBool 0 <=Int B [simplification]
  rule [int-rhs-ineq]: 0 <=Int A >>Int B => true requires 0 <=Int A andBool 0 <=Int B [simplification]
```

## Int Expression Simplifications for Bytes

### Shift Left for Bytes

```k
  rule [int-lsh-bytes-lookup]: B:Bytes[I:Int] <<Int Y => Bytes2Int(padLeftBytes(substrBytes(B, I, I +Int 1), Y /Int 8, 0), LE, Unsigned)
    requires 0 <=Int Y andBool Y modInt 8 ==Int 0
    [simplification, preserves-definedness]
  rule [int-lsh-bytes2int]: Bytes2Int(B, LE, Unsigned) <<Int Y => Bytes2Int(padLeftBytes(B, Y /Int 8, 0), LE, Unsigned)
    requires 0 <=Int Y andBool Y modInt 8 ==Int 0
    [simplification, preserves-definedness]
```

### Shift Right for Bytes

```k
  rule [int-rsh-substrbytes]: Bytes2Int(substrBytes(B, I, J), LE, Unsigned) >>Int Y => Bytes2Int(substrBytes(B, I +Int Y /Int 8, J), LE, Unsigned)
    requires 0 <=Int Y andBool Y modInt 8 ==Int 0 andBool I +Int Y /Int 8 <=Int J
    [simplification, preserves-definedness]
```

### |Int for Bytes

```k
  rule [int-or-bytes-1]: Bytes2Int(b"\x00" +Bytes X, LE, Unsigned) |Int Bytes2Int(Y, _, Unsigned) => Bytes2Int(Y +Bytes X, LE, Unsigned)
    requires lengthBytes(Y) ==Int 1
    [simplification]
  rule [int-or-bytes-2]: Bytes2Int(b"\x00\x00" +Bytes X, LE, Unsigned) |Int Bytes2Int(Y, LE, Unsigned) => Bytes2Int(Y +Bytes X, LE, Unsigned)
    requires lengthBytes(Y) ==Int 2
    [simplification]
  rule [int-or-bytes-3]: Bytes2Int(b"\x00\x00\x00" +Bytes X, LE, Unsigned) |Int Bytes2Int(Y, LE, Unsigned) => Bytes2Int(Y +Bytes X, LE, Unsigned)
    requires lengthBytes(Y) ==Int 3
    [simplification]
```

```k
endmodule
```

## Copy from EVM semantics

```k
module INT-SIMPLIFICATION-HASKELL [symbolic]
    imports INT-SIMPLIFICATION-COMMON

  // ###########################################################################
  // add, sub: associativity normalization
  // ###########################################################################

    rule A +Int (B +Int C) => (A +Int B) +Int C [symbolic(A, B), concrete(C), simplification(40)]
    rule A +Int (B -Int C) => (A +Int B) -Int C [symbolic(A, B), concrete(C), simplification(40)]
    rule A -Int (B +Int C) => (A -Int B) -Int C [symbolic(A, B), concrete(C), simplification(40)]
    rule A -Int (B -Int C) => (A -Int B) +Int C [symbolic(A, B), concrete(C), simplification(40)]

    rule A +Int (B -Int C) => (A -Int C) +Int B [symbolic(A, C), concrete(B), simplification(40)]
    rule A -Int (B -Int C) => (A +Int C) -Int B [symbolic(A, C), concrete(B), simplification(40)]

    rule (A +Int B) +Int C => (A +Int C) +Int B [concrete(B), symbolic(A, C), simplification(40)]
    rule (A +Int B) -Int C => (A -Int C) +Int B [concrete(B), symbolic(A, C), simplification(40)]
    rule (A -Int B) +Int C => (A +Int C) -Int B [concrete(B), symbolic(A, C), simplification(40)]
    rule (A -Int B) -Int C => (A -Int C) -Int B [concrete(B), symbolic(A, C), simplification(40)]

    rule (A +Int B) +Int C => A +Int (B +Int C) [concrete(B, C), symbolic(A), simplification(40)]
    rule (A +Int B) -Int C => A +Int (B -Int C) [concrete(B, C), symbolic(A), simplification(40)]
    rule (A -Int B) +Int C => A +Int (C -Int B) [concrete(B, C), symbolic(A), simplification(40)]
    rule (A -Int B) -Int C => A -Int (B +Int C) [concrete(B, C), symbolic(A), simplification(40)]

  // ###########################################################################
  // add, sub: comparison normalization
  // ###########################################################################

    rule A +Int B   <Int C => A  <Int C -Int B [concrete(B, C), symbolic(A), simplification(45)]
    rule A +Int B  <=Int C => A <=Int C -Int B [concrete(B, C), symbolic(A), simplification(45)]
    rule A +Int B   >Int C => A  >Int C -Int B [concrete(B, C), symbolic(A), simplification(45)]
    rule A +Int B  >=Int C => A >=Int C -Int B [concrete(B, C), symbolic(A), simplification(45)]

    rule A +Int B   <Int C => B  <Int C -Int A [concrete(A, C), symbolic(B), simplification(45)]
    rule A +Int B  <=Int C => B <=Int C -Int A [concrete(A, C), symbolic(B), simplification(45)]
    rule A +Int B   >Int C => B  >Int C -Int A [concrete(A, C), symbolic(B), simplification(45)]
    rule A +Int B  >=Int C => B >=Int C -Int A [concrete(A, C), symbolic(B), simplification(45)]

    rule A -Int B   <Int C => A  <Int C +Int B [concrete(B, C), symbolic(A), simplification(45)]
    rule A -Int B  <=Int C => A <=Int C +Int B [concrete(B, C), symbolic(A), simplification(45)]
    rule A -Int B   >Int C => A  >Int C +Int B [concrete(B, C), symbolic(A), simplification(45)]
    rule A -Int B  >=Int C => A >=Int C +Int B [concrete(B, C), symbolic(A), simplification(45)]

    rule A -Int B   <Int C => A -Int C  <Int B [concrete(A, C), symbolic(B), simplification(45)]
    rule A -Int B  <=Int C => A -Int C <=Int B [concrete(A, C), symbolic(B), simplification(45)]
    rule A -Int B   >Int C => A -Int C  >Int B [concrete(A, C), symbolic(B), simplification(45)]
    rule A -Int B  >=Int C => A -Int C >=Int B [concrete(A, C), symbolic(B), simplification(45)]

    rule A   <Int B +Int C => A -Int B  <Int C [concrete(A, B), symbolic(C), simplification(45)]
    rule A  <=Int B +Int C => A -Int B <=Int C [concrete(A, B), symbolic(C), simplification(45)]
    rule A   >Int B +Int C => A -Int B  >Int C [concrete(A, B), symbolic(C), simplification(45)]
    rule A  >=Int B +Int C => A -Int B >=Int C [concrete(A, B), symbolic(C), simplification(45)]

    rule A   <Int B +Int C => A -Int C  <Int B [concrete(A, C), symbolic(B), simplification(45)]
    rule A  <=Int B +Int C => A -Int C <=Int B [concrete(A, C), symbolic(B), simplification(45)]
    rule A   >Int B +Int C => A -Int C  >Int B [concrete(A, C), symbolic(B), simplification(45)]
    rule A  >=Int B +Int C => A -Int C >=Int B [concrete(A, C), symbolic(B), simplification(45)]

    rule A   <Int B -Int C => C  <Int B -Int A [concrete(A, B), symbolic(C), simplification(45)]
    rule A  <=Int B -Int C => C <=Int B -Int A [concrete(A, B), symbolic(C), simplification(45)]
    rule A   >Int B -Int C => C  >Int B -Int A [concrete(A, B), symbolic(C), simplification(45)]
    rule A  >=Int B -Int C => C >=Int B -Int A [concrete(A, B), symbolic(C), simplification(45)]

    rule A   <Int B -Int C => A +Int C  <Int B [concrete(A, C), symbolic(B), simplification(45)]
    rule A  <=Int B -Int C => A +Int C <=Int B [concrete(A, C), symbolic(B), simplification(45)]
    rule A   >Int B -Int C => A +Int C  >Int B [concrete(A, C), symbolic(B), simplification(45)]
    rule A  >=Int B -Int C => A +Int C >=Int B [concrete(A, C), symbolic(B), simplification(45)]

    rule A +Int B  ==Int C => A ==Int C -Int B [concrete(B, C), symbolic(A), simplification(45), comm]
    rule A +Int B  ==Int C => B ==Int C -Int A [concrete(A, C), symbolic(B), simplification(45), comm]
    rule A -Int B  ==Int C => A ==Int C +Int B [concrete(B, C), symbolic(A), simplification(45), comm]
    rule A -Int B  ==Int C => A -Int C ==Int B [concrete(A, C), symbolic(B), simplification(45), comm]

    rule { A +Int B #Equals C } => { A #Equals C -Int B } [concrete(B, C), symbolic(A), simplification(45), comm]
    rule { A +Int B #Equals C } => { B #Equals C -Int A } [concrete(A, C), symbolic(B), simplification(45), comm]
    rule { A -Int B #Equals C } => { A #Equals C +Int B } [concrete(B, C), symbolic(A), simplification(45), comm]
    rule { A -Int B #Equals C } => { A -Int C #Equals B } [concrete(A, C), symbolic(B), simplification(45), comm]

    rule A +Int B  <Int C +Int D => A -Int C  <Int D -Int B [concrete(B, D), symbolic(A, C), simplification(45)]
    rule A +Int B <=Int C +Int D => A -Int C <=Int D -Int B [concrete(B, D), symbolic(A, C), simplification(45)]
    rule A +Int B  >Int C +Int D => A -Int C  >Int D -Int B [concrete(B, D), symbolic(A, C), simplification(45)]
    rule A +Int B >=Int C +Int D => A -Int C >=Int D -Int B [concrete(B, D), symbolic(A, C), simplification(45)]

    rule A +Int B ==Int A        => B        ==Int 0        [simplification(40)]
    rule A +Int B ==Int B        => A        ==Int 0        [simplification(40)]
    rule A +Int B ==Int C +Int B => A        ==Int C        [simplification(40)]
    rule A +Int B ==Int C +Int D => A -Int C ==Int D -Int B [simplification(45), symbolic(A, C), concrete(B, D)]

    rule { A +Int B #Equals A        } => { B        #Equals 0 }        [simplification(40)]
    rule { A +Int B #Equals B        } => { A        #Equals 0 }        [simplification(40)]
    rule { A +Int B #Equals C +Int B } => { A        #Equals C        } [simplification(40)]
    rule { A +Int B #Equals C +Int D } => { A -Int C #Equals D -Int B } [simplification(45), symbolic(A, C), concrete(B, D)]

endmodule

module INT-SIMPLIFICATION-COMMON
    imports INT
    imports BOOL

  // ###########################################################################
  // add, sub
  // ###########################################################################

  // 2 terms
    rule A -Int A => 0 [simplification]
    rule A -Int 0 => A [simplification]
    rule 0 +Int A => A [simplification]
    rule A +Int 0 => A [simplification]

  // 3 terms
    rule  (A +Int  B) -Int B  => A [simplification]
    rule  (A -Int  B) +Int B  => A [simplification]
    rule   A -Int (A  -Int B) => B [simplification]
    rule   A +Int (B  -Int A) => B [simplification]
    rule  (A +Int  B) -Int A  => B [simplification]

  // 4 terms
    // NOTE: these rules appear to be necessary for tests/specs/benchmarks/ecrecoverloop02-sig1-invalid-spec.k
    rule  (A +Int B) +Int (C  -Int A) => B +Int C [simplification]
    rule  (A +Int B) -Int (A  +Int C) => B -Int C [simplification]
    rule  (A +Int B) -Int (C  +Int A) => B -Int C [simplification]
    rule  (A +Int B) +Int (C  -Int B) => A +Int C [simplification]
    rule  (A -Int B) -Int (C  -Int B) => A -Int C [simplification]
    rule ((A -Int B) -Int  C) +Int B  => A -Int C [simplification]

  // 5 terms
    // NOTE: required for `tests/specs/functional/infinite-gas-spec.k.prove` (haskell)
    rule   (A +Int  B  +Int C)  -Int (A  +Int D) =>  B +Int (C  -Int D) [simplification]
    rule   (C +Int (A  -Int D)) +Int (B  -Int A) =>  C +Int (B  -Int D) [simplification]
    rule (((A -Int  B) -Int C)  -Int  D) +Int B  => (A -Int  C) -Int D  [simplification]

  // ###########################################################################
  // mul
  // ###########################################################################

    rule A *Int B => B *Int A [simplification, symbolic(A), concrete(B)]

    rule 1 *Int A => A [simplification]
    rule 0 *Int _ => 0 [simplification]

    rule (A *Int C) +Int (B *Int C) => (A +Int B) *Int C [simplification]
    rule (A *Int C) -Int (B *Int C) => (A -Int B) *Int C [simplification]

    rule (E *Int A) +Int B +Int C +Int D +Int (F *Int A) => ((E +Int F) *Int A) +Int B +Int C +Int D [simplification]

  // ###########################################################################
  // div
  // ###########################################################################

    rule A /Int 1 => A  [simplification, preserves-definedness]

    // safeMath mul check c / a == b where c == a * b
    rule (A *Int B) /Int A => B requires notBool A ==Int 0 [simplification, preserves-definedness]
    rule (B *Int A) /Int A => B requires notBool A ==Int 0 [simplification, preserves-definedness]

    rule ((A *Int B) /Int C) /Int B => A /Int C requires 0 <Int B andBool 0 <Int C [simplification, preserves-definedness]
    rule ((A *Int B) /Int C) /Int A => B /Int C requires 0 <Int A andBool 0 <Int C [simplification, preserves-definedness]

    rule (A *Int B) /Int C => B *Int (A /Int C)
      requires notBool C ==Int 0 andBool A modInt C ==Int 0
      [simplification, concrete(A, C), preserves-definedness]

    rule (A *Int B) /Int C <=Int D => true
      requires 0 <=Int A andBool 0 <=Int B andBool 0 <Int C andBool A <=Int D andBool B <=Int C
      [simplification, preserves-definedness]

  // ###########################################################################
  // mod
  // ###########################################################################

    rule A modInt B => A requires 0 <=Int A andBool A <Int B [simplification, preserves-definedness]

  // ###########################################################################
  // max, min
  // ###########################################################################

    rule [minint-left]:  minInt(A, B) => A requires A <=Int B [simplification]
    rule [minint-right]: minInt(A, B) => B requires B <=Int A [simplification]

    rule [minint-lt]:  minInt(A, B)  <Int C => A  <Int C  orBool B  <Int C [simplification]
    rule [minint-leq]: minInt(A, B) <=Int C => A <=Int C  orBool B <=Int C [simplification]
    rule [minint-gt]:  A  <Int minInt(B, C) => A  <Int B andBool A  <Int C [simplification]
    rule [minint-geq]: A <=Int minInt(B, C) => A <=Int B andBool A <=Int C [simplification]

    rule [minInt-factor-left]:  minInt ( A:Int +Int B:Int, A:Int +Int C:Int ) => A +Int minInt ( B, C ) [simplification]
    rule [minInt-factor-right]: minInt ( A:Int +Int B:Int, C:Int +Int B:Int ) => minInt ( A, C ) +Int B [simplification]

    rule [maxint-left]:  maxInt(A:Int, B:Int) => B requires A <=Int B [simplification]
    rule [maxint-right]: maxInt(A:Int, B:Int) => A requires B <=Int A [simplification]

    rule [maxint-lt]:  maxInt(A:Int, B:Int)  <Int C:Int => A  <Int C andBool B  <Int C [simplification]
    rule [maxint-leq]: maxInt(A:Int, B:Int) <=Int C:Int => A <=Int C andBool B <=Int C [simplification]
    rule [maxint-gt]:  A:Int  <Int maxInt(B:Int, C:Int) => A  <Int B  orBool A  <Int C [simplification]
    rule [maxint-geq]: A:Int <=Int maxInt(B:Int, C:Int) => A <=Int B  orBool A <=Int C [simplification]

    rule [maxInt-factor-left]:  maxInt ( A:Int +Int B:Int, A:Int +Int C:Int ) => A +Int maxInt ( B, C ) [simplification]
    rule [maxInt-factor-right]: maxInt ( A:Int +Int B:Int, C:Int +Int B:Int ) => maxInt ( A, C ) +Int B [simplification]

  // ###########################################################################
  // inequality
  // ###########################################################################

    rule A +Int B <Int A => false requires 0 <=Int B [simplification]
    rule A +Int B <Int B => false requires 0 <=Int A [simplification]

    rule A <Int A -Int B => false requires 0 <=Int B [simplification]

    rule 0 <Int 1 <<Int A => true requires 0 <=Int A [simplification, preserves-definedness]

    // inequality sign normalization
    rule          A  >Int B  => B  <Int A [simplification]
    rule          A >=Int B  => B <=Int A [simplification]
    rule notBool (A  <Int B) => B <=Int A [simplification]
    rule notBool (A <=Int B) => B  <Int A [simplification]

    rule 0 <=Int A +Int B => true requires 0 <=Int A andBool 0 <=Int B [simplification]
    rule 0 <=Int A *Int B => true requires 0 <=Int A andBool 0 <=Int B [simplification]

    rule A -Int B +Int C <=Int D => false requires D <Int A -Int B andBool 0 <=Int C [simplification]

endmodule
```