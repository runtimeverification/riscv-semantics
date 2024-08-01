#include "simple.h"

START_TEXT
        li x1, 0xFFFFFFFF
        ori x2, x1, 0  // x2 = 0xFFFFFFFF

        li x4, -11      // x4 = -11
        ori x5, x4, -10 // x4 = -11
END_TEXT
