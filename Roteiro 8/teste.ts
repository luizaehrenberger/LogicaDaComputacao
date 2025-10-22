let i:number;
let n:number;
let f:number = 1;
n = readline();
i = 2;
while (i < n + 1) {
  f = f * i;
  i = i + 1;
}
log(f);
