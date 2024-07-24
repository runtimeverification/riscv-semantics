#include "simple.h"

START_TEXT
        addi x1, x0, 1 // x1 = 1
        slti x2, x1, 2 // x2 = 1
        slti x3, x1, 1 // x3 = 0

        addi x4, x0, 1 // x4 = 1
        slti x4, x4, 1 // x4 = 0

        addi x5, x0, -10 // x5 = -10
        slti x6, x5, 1   // x6 = 1
        slti x7, x5, -11 // x7 = 0
END_TEXT
