let number y = 5;
let number x;
let boolean b = true;
let string s = "oi";

x = 2 + 3 * y;          // 17
log(x);                 // 17

let string t = s + " mundo " + x;
log(t);                 // "oi mundo 17"

log(5 == "5");          // false (tipos diferentes)
log(5 === 5);           // true
log("a" != "b");        // true

let string who = "bob";
if (who === "bob") { log("é o bob"); } else { log("não é o bob"); }

let number i = 0;
while (i < 3) {
  log("i=" + i);
  i = i + 1;
}

let number a = 1 + 2 * 3;
log(a);
