# Int Simplifications

```k
module INT-SIMPLIFICATIONS
  imports INT
  imports K-EQUAL
```

## Shift Lemmas

```k
  rule [int-lsh-lsh]: (W0 <<Int N0) <<Int N1 => W0 <<Int (N0 +Int N1)
    [simplification, preserves-definedness]
```

```k
endmodule
```
