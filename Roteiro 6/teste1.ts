// if/else com &&, || e !
x = 10;
y = 3;

{
  // (x > y) && !(y == 0)  =>  (10 > 3) && !(false) => true && true => true
  if ((x > y) && !(y == 0)) {
    log(111);
  } else {
    log(222);
  }
}

{
  // (x < y) || (x == 10) => false || true => true
  if ((x < y) || (x == 10)) {
    log(333);
  } else {
    log(444);
  }
}
