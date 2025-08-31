# quick_test.py
from main import Parser

ok_cases = {
    "3-2": 1,
    "1": 1,
    "11+22-33": 0,
    "4/2+3": 5,
    "3+4/2": 5,
    "(3 + 2) /5": 1,
    "+--++3": 3,
    "3 - -2/4": 3,  # divisão inteira truncando para zero: -2/4 -> 0
    "4/(1+1)*2": 4,
}

err_cases = [
    "*3",
    "3+",
    "",
    "3*/ 3 +",
    "(2*2",
    "1)",
]

def run_ok():
    print("== Casos sem erro ==")
    for src, expected in ok_cases.items():
        got = Parser.run(src)
        status = "OK" if got == expected else "FALHOU"
        print(f"{src:>12} -> got={got} expected={expected} [{status}]")
    print()

def run_err():
    print("== Casos que devem falhar ==")
    for src in err_cases:
        try:
            Parser.run(src)
            print(f"{src!r:>12} -> ERRO ESPERADO, mas parseou!")
        except Exception as e:
            print(f"{src!r:>12} -> Exception: {e}")
    print()

if __name__ == "__main__":
    run_ok()
    run_err()
