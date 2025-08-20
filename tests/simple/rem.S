#include "simple.h"

START_TEXT
	// Test basic signed remainder operations
	li x1, 17    // x1 = 17
	li x2, 5     // x2 = 5
	rem x3, x1, x2  // x3 = 17 % 5 = 2

	// Test negative dividend
	li x4, -17   // x4 = -17
	rem x5, x4, x2  // x5 = -17 % 5 = -2

	// Test negative divisor
	li x6, -5    // x6 = -5
	rem x7, x1, x6  // x7 = 17 % -5 = 2

	// Test both negative
	rem x8, x4, x6  // x8 = -17 % -5 = -2

	// Test division by zero (should return dividend)
	li x9, 0     // x9 = 0
	rem x10, x1, x9  // x10 = 17 % 0 = 17

	// Test overflow case (most negative number % -1)
	li x11, 0x80000000  // x11 = most negative number
	li x12, -1          // x12 = -1
	rem x13, x11, x12   // x13 = most negative % -1 = 0
END_TEXT
