#include "simple.h"

START_TEXT
	li x1, 0xDEADBEEF // x1 = 0xDEADBEEF
	add x2, x1, x0    // x2 = 0xDEADBEEF

	xori x3, x1, -1   // x3 = ~x2
	addi x3, x3, 1    // x3 = ~x2 + 1 = -x2
	li x4, 0xFFFFFFFF // x4 = 0xFFFFFFFF
	add x4, x4, x3    // x4 = 0xFFFFFFFF - x2
	addi x4, x4, 1    // x4 = (0xFFFFFFFF - x2) + 1

	add x5, x2, x4 // x5 = 0xFFFFFFFF + 1 = 0
END_TEXT
