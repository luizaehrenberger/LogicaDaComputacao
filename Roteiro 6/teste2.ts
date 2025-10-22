// soma números ímpares positivos abaixo de n usando while e &&
n = 10;
i = 0;
s = 0;

while ( (i < n) && !(i == n) ) {
  if ( (i % 2) == 1 ) {  // OBS: se não tiver operador %, remova esta linha e a seguinte
    s = s + i;
  }
  i = i + 1;
}

log(s);
