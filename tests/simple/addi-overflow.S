#include "simple.h"

START_TEXT
        lui x1, 0x7FFFF
        addi x1, x1, 2047
        addi x1, x1, 2047
        addi x1, x1, 1
        // x1 contains 2^31 - 1, the largest 32-bit two's complement integer.
        // Setting x2 = x1 + 1 should overflow
        addi x2, x1, 1
END_TEXT
