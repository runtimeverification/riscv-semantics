#include "simple.h"

START_TEXT
        li x1, 0xDEADBEEF
        slli x2, x1, 0  // x2 = 0xDEADBEEF
        slli x3, x1, 4  // x3 = 0xEADBEEF0
        slli x4, x1, 31 // x4 = 0x80000000
END_TEXT
