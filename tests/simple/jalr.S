#include "simple.h"

START_TEXT
	auipc x15, 0     // x15 = PC_4
        addi x15, x15, 5 // x15 = PC_4 + 5
        jalr x1, x15, 7  // x1 = PC_6 + 4, jump to PC_4 + 12 = PC_7
        auipc x2, 0      // x2 = PC_5 = PC_4 + 4 = x1
        sub x3, x1, x2   // x3 = 0

        addi x4, x0, 0   // x4 = 0
	auipc x14, 0     // x14 = PC_11
        jalr x0, x14, 13 // jump to PC_11 + 13 = PC_14
        addi x4, x4, 1   // should be skipped
        nop              // still x4 = 0

        addi x5, x0, 0    // x5 = 0
	auipc x13, 0      // x13 = PC_17
        jalr x0, x13, 20  // jump to PC_17 + 20 = PC_22
        addi x5, x5, 1    // x5 += 1
	auipc x12, 0      // x12 = PC_20
        jalr x0, x12, 16  // jump to PC_20 + 16 = PC_24
	auipc x11, 0      // x11 = PC_22
        jalr x0, x11, -11 // jump to PC_22 - 11 = PC_19
        nop               // now x5 = 1
END_TEXT
