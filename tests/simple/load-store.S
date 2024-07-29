#include "simple.h"

.data
test_data:
        .byte 0x80       // -128 in signed, 128 in unsigned
        .hword 0x8001    // -32767 in signed, 32769 in unsigned
        .word 0x7FFFFFFF // 2147483647

START_TEXT
        la x5, test_data
        la x6, results

        lb x8, 0(x5)
        sw x8, 0(x6)

        lh x9, 1(x5)
        sw x9, 4(x6)

        lw x10, 3(x5)
        sw x10, 8(x6)

        lbu x11, 0(x5)
        sw x11, 12(x6)

        lhu x12, 1(x5)
        sw x12, 16(x6)

        li x13, 0xFF
        sb x13, 0(x5)

        li x14, 0xAAAA
        sh x14, 1(x5)

        li x15, 0xBBBBCCCC
        sw x15, 3(x5)
END_TEXT

MEMORY
results:
        .align 4
        .word 0x0
        .word 0x0
        .word 0x0
        .word 0x0
        .word 0x0
        .word 0x0

