// Demonstra 0/1 para booleanos e operadores lógicos
a = 2;
b = 3;

{
  log(a < b);                 // 1
  log(a === b);               // 0  (use === se seu lexer suportar; senão, troque por ==)
  log(!(a === b));            // 1
  log((a < b) && (b < 10));   // 1
  log((a > b) || (b === 3));  // 1
};

; ;  // linhas vazias são válidas
