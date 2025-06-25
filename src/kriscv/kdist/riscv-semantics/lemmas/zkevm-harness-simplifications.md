# ZKEVM Harness Simplifications

This file contains simplification rules for the [zkevm-harness](https://github.com/runtimeverification/zkevm-harness). Although these simplification rules are not specific to this project, they are rules that were discovered to be needed within this project. However, we currently do not want to perform a comprehensive organization of rules, so we place these rules here for quick addition of simplification rules.

Why not put them in the zkevm-harness repository?
1. We currently do not have an out-of-the-box simplification rule testing framework, so we would need to spend additional time creating a new testing framework in the zkevm-harness repository;
2. These rules actually have some general applicability, but considering performance, we may not need to adopt these rules for all verification targets.

```k
requires "../word.md"
module ZKEVM-HARNESS-SIMPLIFICATIONS [symbolic]
  imports INT
  imports BYTES
  imports K-EQUAL
  imports BOOL
  imports WORD
```

## MSTORE

The following rules are required to prove the claim in `tests/integration/test-data/specs/zkevm-mstore.k`:

```k
rule 0 <Int (0 -Int Bool2Word(4294967295 <Int X)) &Int 4294967295 |Int X &Int 4294967295 => true requires 0 <Int X [simplification(45)]

rule 0 <Int A +Int B => true requires 0 <=Int A andBool 0 <Int B [simplification(45)]
rule 0 <Int A +Int B => true requires 0 <Int A andBool 0 <=Int B [simplification]

rule Bytes2Int (B:Bytes +Bytes b"\x00\x00\x00" , LE , Unsigned ) => Bytes2Int (B, LE, Unsigned) [simplification(45)]
```

The following additional rules would be needed to handle the 5th register in the zkevm-mstore claim, but they interfere with the targeted rewriting of the 4th register. Therefore, they are not included in the module above:
```
rule X <Int Bytes2Int(B, _, Unsigned) => false requires 2 ^Int (lengthBytes(B) *Int 8) -Int 1 <=Int X [simplification]
rule A <Int B +Int C => A -Int C <Int B [simplification, concrete(A,C), symbolic(B)]
rule 0 |Int X => X [simplification]
```

To handle the 6-th and 7-th registers in the zkevm-mstore claim, we need the following rules:
```k
rule Bool2Word(B) ==Int 0 => notBool B [simplification]
rule Bool2Word(B) ==Int 1 => B [simplification]
```

```k
endmodule
```