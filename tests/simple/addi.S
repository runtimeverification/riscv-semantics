#include "simple.h"

START_TEXT
        addi x1, x0, 8 // x1 = 8
        addi x1, x1, 8 // x1 = 16
        addi x2, x1, 0 // x2 = 16

        lui x3, 0x7FFFF
        addi x3, x3, 2047
        addi x3, x3, 2047
        addi x3, x3, 1
        // x3 contains 2^31 - 1, the largest 32-bit two's complement integer.
        // Setting x2 = x1 + 1 should overflow
        addi x4, x3, 1
END_TEXT
