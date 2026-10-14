<<<<<<< HEAD
# QFF 2026 Phase 1 — Quantum-Safe Secure Channel (PQC + Processor A/B)

This repository contains two **separate, reproducible experiments** for the selected quantum-safe cryptography work:

1. **Cryptographic application:** ML-KEM-768 for shared-secret establishment, ML-DSA-65 and Falcon-512 for signatures, and AES-256-GCM for authenticated message encryption.
2. **QFF Processor A/B architecture benchmark:** Qiskit simulation of the guide's 5-qubit Processor A and 9-qubit Processor B coupling graphs, using the specified basis gates, noise rates, transpilation seed/optimization level, and 4096 shots.

## Important interpretation

ML-KEM, ML-DSA, Falcon, and AES-GCM are classical cryptographic algorithms. They do **not** execute as quantum circuits on Processor A or Processor B. The Qiskit experiment compares a test quantum circuit mapped to the two reference architectures. The cryptographic benchmark measures the algorithms on the computer running Python. Results from these two experiments are reported separately; do not describe crypto timings as measurements on qubits.

The guide permits participant-defined graphs. This project uses the listed reference graph for Processor A (branching tree) and the listed 12-edge graph for Processor B. The synthetic noise rates are the guide's stated rates: 1-qubit depolarizing p=0.001, CX depolarizing p=0.005, and readout error p=0.01. Both processors use the same rates.

## Repository map

- `processors/processor_A.json`, `processors/processor_B.json`: processor configurations
- `src/processors.py`: graph/noise configuration loaders
- `src/routing.py`: deterministic transpilation
- `src/problem.py`: repeatable 5-qubit architecture-probe circuit
- `src/metrics.py`: circuit metrics and total-variation distance
- `src/visualization.py`: topology and benchmark plots
- `main.py`: runs Processor A/B benchmark and exports tables/figures
- `benchmark_crypto.py`: benchmarks ML-KEM-768, ML-DSA-65, Falcon-512, and the secure-channel flow
- `algorithms/`: cryptographic wrappers using `liboqs-python`
- `encryption/aes_gcm.py`: AES-256-GCM helper
- `tests/`: smoke tests for cryptographic functions
- `results/tables/`, `results/figures/`: generated outputs

## Setup (Windows PowerShell)

Use Python 3.11 if possible. From the extracted project directory:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`liboqs-python` requires a compatible `liboqs` native library. Since your previous environment already imported `oqs`, first try running these scripts from that same environment. If `import oqs` fails in a fresh environment, follow the official liboqs-python/liboqs installation instructions and configure the library path for your installation. Do not copy a virtual environment between machines.

## Run in this order

```powershell
python check_environment.py
python test_ml_kem.py
python test_ml_dsa.py
python test_falcon.py
python main.py
python benchmark_crypto.py --iterations 20
```

`main.py` writes processor metrics, ideal/noisy counts, and charts. `benchmark_crypto.py` writes raw per-iteration data and summary CSV/JSON/plots. Increase `--iterations` for more stable timing estimates.

## Reproducibility notes

- Transpilation uses optimization level 1 and seed 42.
- Quantum simulator shots: 4096.
- Processor graph and noise assumptions are explicitly stored in JSON.
- Crypto timing is measured with `time.perf_counter`; timing results are host-dependent and are not pre-filled or fabricated.
- Memory reporting uses Python `tracemalloc` (Python-managed allocations), not total native `liboqs` process memory. Treat it as an approximate metric.
- SWAP metric means explicit `swap` instructions remaining in the transpiled circuit. Routing may instead be represented by additional CX gates; use CX count and depth together when interpreting routing overhead.
=======
# QuantumSafeSecureChannel
Quantum-Safe Secure Channel using Post-Quantum Cryptography
>>>>>>> ce1bb96f73cc1a4f58f066b33eefd8ea13e29ad4
