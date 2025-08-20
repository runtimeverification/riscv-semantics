#include "simple.h"

START_TEXT
	// Test basic unsigned remainder operations
	li x1, 17    // x1 = 17
	li x2, 5     // x2 = 5
	remu x3, x1, x2  // x3 = 17 % 5 = 2

	// Test large unsigned values
	li x4, 0xFFFFFFFF  // x4 = 0xFFFFFFFF (large unsigned)
	li x5, 10          // x5 = 10
	remu x6, x4, x5    // x6 = 0xFFFFFFFF % 10 = 5

	// Test division by zero (should return dividend)
	li x7, 0     // x7 = 0
	remu x8, x1, x7  // x8 = 17 % 0 = 17

	// Test large divisor
	li x9, 0x80000000  // x9 = 0x80000000
	li x10, 0x40000000 // x10 = 0x40000000
	remu x11, x9, x10  // x11 = 0x80000000 % 0x40000000 = 0

	// Test remainder equals dividend
	li x12, 100        // x12 = 100
	li x13, 200        // x13 = 200
	remu x14, x12, x13 // x14 = 100 % 200 = 100
END_TEXT
