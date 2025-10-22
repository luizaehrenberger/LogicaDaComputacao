section .data
  format_out: db "%d", 10, 0 ; format do printf
  format_in: db "%d", 0 ; format do scanf
  scan_int: dd 0 ; 32-bits integer

section .text

  extern printf ; usar _printf para Windows
  extern scanf  ; usar _scanf para Windows
  ; extern _ExitProcess@4 ; usar para Windows
  global _start ; início do programa

_start:
  push ebp       ; guarda o EBP
  mov ebp, esp   ; zera a pilha

  ; aqui começa o codigo gerado:

  sub esp, 4 ; var i int [EBP-4]
  sub esp, 4 ; var n int [EBP-8]
  sub esp, 4 ; var f int [EBP-12]
  mov eax, 1
  mov [ebp-12], eax
  push dword scan_int
  push dword format_in
  call scanf
  add esp, 8
  mov eax, dword [scan_int]
  mov [ebp-8], eax
  mov eax, 2
  mov [ebp-4], eax
loop_30:
  mov eax, 1
  push eax
  mov eax, [ebp-8]
  pop ecx
  add eax, ecx
  push eax
  mov eax, [ebp-4]
  pop ecx
  cmp eax, ecx
  mov eax, 0
  mov ecx, 1
  cmovl eax, ecx
  cmp eax, 0
  je exit_30
  mov eax, [ebp-4]
  push eax
  mov eax, [ebp-12]
  pop ecx
  imul ecx
  mov [ebp-12], eax
  mov eax, 1
  push eax
  mov eax, [ebp-4]
  pop ecx
  add eax, ecx
  mov [ebp-4], eax
  jmp loop_30
exit_30:
  mov eax, [ebp-12]
  push eax
  push dword format_out
  call printf
  add esp, 8
  ; aqui termina o código gerado

  mov esp, ebp   ; reestabelece a pilha
  pop ebp

  ; chamada da interrupcao de saida (Linux)
  mov eax, 1   
  xor ebx, ebx 
  int 0x80     
  ; Para Windows:
  ; push dword 0        
  ; call _ExitProcess@4 
