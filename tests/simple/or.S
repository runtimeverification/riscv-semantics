#include "simple.h"

START_TEXT
        // Same as ori.S, but put immediates in registers
        addi x15, x0, 0
        addi x14, x0, -10

        li x1, 0xFFFFFFFF
        or x2, x1, x15  // x2 = 0xFFFFFFFF

        li x4, -11     // x4 = -11
        or x5, x4, x14 // x4 = -11
END_TEXT
