// Conta regressiva com ramificação
n = 5;
while (n > 0) {
  if ((n % 2) == 0) {
    log(n + 100);  // par => imprime deslocado
  } else {
    log(n);        // ímpar => imprime normal
  }
  n = n - 1;
}
log(0);
