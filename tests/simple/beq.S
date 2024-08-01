#include "simple.h"

START_TEXT
        addi x15, x0, 0
        beq x0, x0, .+8
        addi x15, x0, 1

        addi x14, x0, 0
        addi x2, x0, 1
        beq x0, x2, .+8
        addi x14, x0, 1
        nop
END_TEXT
