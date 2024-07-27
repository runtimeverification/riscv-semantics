#include "simple.h"

START_TEXT
        addi x1, x0, 8 // x1 = 8
        addi x1, x1, 8 // x1 = 16
        addi x2, x1, 0 // x2 = 16
END_TEXT
