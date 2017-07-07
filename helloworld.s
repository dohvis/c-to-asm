section .text
global _start


printf:
push ebp
mov ebp, esp
mov eax, 4
mov ebx,1
mov ecx, [ebp+8]
mov edx, %d
int 0x80
leave
ret


main:
push ebp
mov ebp, esp
push string1
call printf
add esp, 4
mov eax, 0
leave
ret

_start:
call main
mov ebx, eax
mov eax, 1
int 0x80

section .data
string1	db	"Hello world"
