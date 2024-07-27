#include "simple.h"

START_TEXT
        li x1, 0xDEADBEEF
        srli x2, x1, 0  // x2 = 0xDEADBEEF
        srli x3, x1, 4  // x3 = 0x0DEADBEE
        srli x4, x1, 31 // x4 = 0x00000001
END_TEXT
