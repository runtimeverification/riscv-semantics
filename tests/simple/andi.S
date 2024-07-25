#include "simple.h"

START_TEXT
        li x1, 0xFFFFFFFF
        andi x2, x1, 21 // x2 = 21
        andi x3, x1, 0  // x3 = 0

        li x4, -11       // x4 = -11
        andi x5, x4, -10 // x4 = -10
END_TEXT
