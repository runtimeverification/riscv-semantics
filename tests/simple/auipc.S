#include "simple.h"

START_TEXT
        auipc x0, 0x10

        auipc x1, 0       // x1 = PC of this line
        auipc x2, 0       // x2 = x1 + 4
        addi x0, x0, 0
        auipc x3, 0x80000 // x3 = x1 + 12 + 0x80000000 = x1 + 0x8000000C

        xori x4, x1, -1  // x4 = ~x1
        addi x4, x4, 1   // x4 = ~x1 + 1 = -x1

        add x2, x2, x4 // x2 = 4
        add x3, x3, x4 // x3 = 0x8000000C
END_TEXT
