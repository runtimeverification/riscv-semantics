#pragma once

#define START_TEXT \
  .text;           \
  .globl _start;   \
  _start:

#define END_TEXT \
  .globl _halt;  \
  _halt:         \
        nop;

#define HALT \
        j _halt;
