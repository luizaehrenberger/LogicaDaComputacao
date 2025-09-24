// Demonstra booleanos como 0/1
a = 2;
b = 3;

{
  log(a < b);   // 1
  log(a == b);  // 0
  log(!(a == b)); // 1
  log((a < b) && (b < 10)); // 1
  log((a > b) || (b == 3)); // 1
};

; ; ;  // linhas vazias válidas
