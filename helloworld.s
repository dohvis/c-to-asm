section .text
global _start

printf:
push ebp
mov ebp, esp
mov eax, 4
mov ebx,1
mov ecx, [ebp+8]
mov edx, 13
int 0x80
leave
ret

_start:
push string1
call printf
add esp, 4

exit:
mov eax, 1
int 0x80

section .data
string1	db	"Hello world"
string1_size	equ	$-string1
