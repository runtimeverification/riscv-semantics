#include "simple.h"

START_TEXT
        li x1, 0xDEADBEEF // x1 = 0xDEADBEEF
        add x2, x1, x0    // x2 = 0xDEADBEEF

        sub x3, x0, x2    // x3 = -x2

        xori x4, x2, -1   // x4 = ~x2
        addi x4, x4, 1    // x4 = ~x2 + 1 = -x2

        sub x5, x4, x3    // x5 = 0
END_TEXT
