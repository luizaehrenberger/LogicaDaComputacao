import subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
runner = [sys.executable, "-m", "src.main"]

tests = [
    ("ok_exemplo.ts", True, ["7", "3", "5"]),
    ("ok_recursao.ts", True, ["120"]),
    ("err_args_qtd.ts", False, ["Chamada de 'inc'"]),
    ("err_tipo_arg.ts", False, ["Tipo inválido", "show"]),
    ("err_func_inexistente.ts", False, ["Identificador 'foo'"]),
    ("err_escopo.ts", False, ["Identificador 'x'"]),
]

ok = 0
for fname, should_pass, expects in tests:
    path = ROOT / "programas" / fname
    print(f"==> {fname}")
    proc = subprocess.run(runner + [str(path)], capture_output=True, text=True)
    out = proc.stdout.strip()
    err = proc.stderr.strip()
    success = (proc.returncode == 0)

    if should_pass and success and all(e in out for e in expects):
        print("   PASS (stdout):")
        print("   " + out.replace("\n", "\n   "))
        ok += 1
    elif (not should_pass) and (not success) and all(e in err for e in expects):
        print("   PASS (erro esperado):")
        print("   " + err.replace("\n", "\n   "))
        ok += 1
    else:
        print("   FAIL")
        print("   returncode:", proc.returncode)
        print("   stdout:\n   " + (out or "<vazio>").replace("\n", "\n   "))
        print("   stderr:\n   " + (err or "<vazio>").replace("\n", "\n   "))

print(f"\n{ok}/{len(tests)} testes passaram.")
sys.exit(0 if ok == len(tests) else 1)
