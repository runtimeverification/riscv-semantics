#include "simple.h"

START_TEXT
        li x1, 0xFFFFFFFF
        xori x2, x1, 0  // x2 = 0xFFFFFFFF
        xori x3, x1, 1  // x2 = 0xFFFFFFFE

        li x4, -11       // x4 = -11
        xori x5, x4, -10 // x4 = 3
END_TEXT
