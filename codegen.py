from __future__ import annotations
from typing import List

class Code:
    instructions: List[str] = []

    @staticmethod
    def reset() -> None:
        Code.instructions = []

    @staticmethod
    def append(code: str) -> None:
        Code.instructions.append(code)

    @staticmethod
    def dump(filename: str) -> None:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(
                "section .data\n"
                "  format_out: db \"%d\", 10, 0 ; format do printf\n"
                "  format_in:  db \"%d\", 0    ; format do scanf\n"
                "  scan_int:   dd 0            ; 32-bits integer\n"
                "\n"
                "section .text\n\n"
                "  extern printf ; usar _printf para Windows\n"
                "  extern scanf  ; usar _scanf  para Windows\n"
                "  ; extern _ExitProcess@4 ; para Windows\n"
                "  global _start ; início do programa\n\n"
                "_start:\n"
                "  push ebp       ; guarda o EBP\n"
                "  mov  ebp, esp  ; zera a pilha\n"
                "\n"
                "  ; aqui começa o codigo gerado:\n\n"
            )
            if Code.instructions:
                f.write("\n".join(Code.instructions))
                f.write("\n")
            f.write(
                "  ; aqui termina o código gerado\n\n"
                "  mov esp, ebp   ; reestabelece a pilha\n"
                "  pop ebp\n"
                "\n"
                "  ; interrupção de saída (Linux)\n"
                "  mov eax, 1\n"
                "  xor ebx, ebx\n"
                "  int 0x80\n"
                "  ; Windows:\n"
                "  ; push dword 0\n"
                "  ; call _ExitProcess@4\n"
            )
