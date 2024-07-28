#include "simple.h"

START_TEXT
        // Same as xori.S, but put immediates in registers
        addi x15, x0, 0
        addi x14, x0, 1
        addi x13, x0, -10

        li x1, 0xFFFFFFFF
        xor x2, x1, x15  // x2 = 0xFFFFFFFF
        xor x3, x1, x14  // x2 = 0xFFFFFFFE

        li x4, -11      // x4 = -11
        xor x5, x4, x13 // x4 = 3
END_TEXT
