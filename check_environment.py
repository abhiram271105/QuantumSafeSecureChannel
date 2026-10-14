import sys, platform, importlib
print("Python:", sys.version)
print("Platform:", platform.platform())
for module in ("qiskit", "qiskit_aer", "numpy", "matplotlib", "networkx", "cryptography", "oqs"):
    try:
        m = importlib.import_module(module)
        print(f"{module}: OK", getattr(m, "__version__", ""))
    except Exception as exc:
        print(f"{module}: FAILED — {exc}")
