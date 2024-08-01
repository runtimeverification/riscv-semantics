#include "simple.h"

START_TEXT
        // Same as sltu.S, but put immediates in registers
        addi x15, x0, 2
        addi x14, x0, 1
        addi x13, x0, -11

        addi x1, x0, 1   // x1 = 1
        sltu x2, x1, x15 // x2 = 1
        sltu x3, x1, x14 // x3 = 0

        addi x4, x0, 1   // x4 = 1
        sltu x4, x4, x14 // x4 = 0

        addi x5, x0, -10 // x5 = -10
        sltu x6, x5, x14 // x6 = 0
        sltu x7, x5, x13 // x7 = 0
END_TEXT
