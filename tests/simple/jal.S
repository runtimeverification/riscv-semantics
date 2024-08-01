#include "simple.h"

START_TEXT
        jal x1, .+4    // x1 = PC_4 + 4
        auipc x2, 0    // x2 = PC_5 = PC_4 + 4 = x1
        sub x3, x1, x2 // x3 = 0

        addi x4, x0, 0 // x4 = 0
        jal x0, .+8
        addi x4, x4, 1 // should be skipped
        nop            // still x4 = 0

        addi x5, x0, 0 // x5 = 0
        jal x0, .+12   // jump to line 18
        addi x5, x5, 1 // x5 += 1
        jal x0, .+8    // jump to line 19
        jal x0, .-8    // jump to line 16
        nop            // now x5 = 1
END_TEXT
