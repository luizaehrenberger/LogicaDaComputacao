let b:number = 5;

function soma(x:number, y:number): number {
  let a:number;
  a = x + y;
  log(a); // 7
  return a;
}

function main(): void {
  let a:number;
  {
    let b:number;
    a = 3;
    b = soma(a, 4);
    log(b); // 7
  }
  log(a); // 3
  log(b); // 5
}
main();
