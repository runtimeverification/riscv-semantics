.text
.globl _start	
_start:
	lui x0, 0x10
	lui x1, 0x80000
	lui x2, 0x70000
.globl _halt
_halt:
	nop
