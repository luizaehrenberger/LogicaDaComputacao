function fat(n:number): number {
  if (n === 0) { return 1; }
  else { return n * fat(n - 1); }
}
function main(): void {
  let x:number;
  x = fat(5);
  log(x);
}
main();
