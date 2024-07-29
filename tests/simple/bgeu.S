#include "simple.h"

START_TEXT
        addi x15, x0, 0
        bgeu x0, x0, .+8
        addi x15, x0, 1

        addi x14, x0, 0
        addi x2, x0, 1
        bgeu x0, x2, .+8
        addi x14, x0, 1

        addi x13, x0, 0
        addi x3, x0, -1
        bgeu x0, x3, .+8
        addi x13, x0, 1

        addi x12, x0, 0
        bgeu x3, x0, .+8
        addi x12, x0, 1
END_TEXT
