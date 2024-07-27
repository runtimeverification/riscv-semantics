#include "simple.h"

START_TEXT
        li x1, 0xDEADBEEF
        srai x2, x1, 0  // x2 = 0xDEADBEEF
        srai x3, x1, 4  // x3 = 0xFDEADBEE
        srai x4, x1, 31 // x4 = 0xFFFFFFFF
END_TEXT
