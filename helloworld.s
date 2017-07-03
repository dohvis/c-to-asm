section .text

_start:
push string1
call printf
add esp, 4

printf:
push ebp
mov ebp, esp
mov eax, 4mov ebx,1
mov ecx, [ebp+8]
mov edx,size
int 0x80
leave
let

exit:
mov eax, 1
int 0x80

section .data
string1	db	"hello world"
string1_size	equ	$-string1
