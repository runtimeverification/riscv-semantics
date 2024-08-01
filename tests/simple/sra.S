#include "simple.h"
START_TEXT
        li x15, 0xFFFFFFE0 // x15[4:0] = 0
        li x14, 0xFFFFFFE4 // x14[4:0] = 4
        li x13, 0xFFFFFFFF // x13[4:0] = 31

        li x1, 0xDEADBEEF
        sra x2, x1, x15 // x2 = 0xDEADBEEF
        sra x3, x1, x14 // x3 = 0xFDEADBEE
        sra x4, x1, x13 // x4 = 0xFFFFFFFF
END_TEXT
