#include "simple.h"

START_TEXT
        // Same as andi.S, but put immediates in registers
        addi x15, x0, 21
        addi x14, x0, 0
        addi x13, x0, -10

        li x1, 0xFFFFFFFF
        and x2, x1, x15 // x2 = 21
        and x3, x1, x14 // x3 = 0

        li x4, -11      // x4 = -11
        and x5, x4, x13 // x4 = -10
END_TEXT
