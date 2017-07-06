# c-to-asm

[![CircleCI](https://circleci.com/gh/nerogit/c-to-asm.svg?style=svg)](https://circleci.com/gh/nerogit/c-to-asm)

## How to run
```sh
python3 c2asm.py helloworld.c
nasm -f elf helloworld.s
ld -melf_i386 helloworld.o -o helloworld
chmod +x helloworld
./helloworld
```

Then

```c
int main(  ) {
    printf("Hello world");
    return 0;
}
```



```asm
section .text
global _start


printf:
    push ebp
    mov ebp, esp
    mov eax, 4
    mov ebx,1
    mov ecx, [ebp+8]
    mov edx, 13
    int 0x80 ; write(1, string1, strlen(string1))
    leave
    ret


main:
    push ebp
    mov ebp, esp
    push string1
    call printf ; printf("Hello world")
    add esp, 4
    mov eax, 0 ; return 0
    leave
    ret

_start:
    call main
    mov ebx, eax
    mov eax, 1
    int 0x80 ; exit(main())

section .data
string1	db	"Hello world"

```

