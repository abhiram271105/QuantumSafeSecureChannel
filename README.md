# QFF 2026 Phase 1 — Quantum-Safe Secure Channel (PQC + Processor A/B)

This project consists of two separate experiments related to quantum-safe cryptography and quantum processor architecture benchmarking.

1. **Quantum-Safe Cryptographic Application:** Uses ML-KEM-768 for shared-secret establishment, ML-DSA-65 and Falcon-512 for digital signatures, and AES-256-GCM for authenticated message encryption.
2. **Processor A/B Architecture Benchmark:** Uses Qiskit to simulate quantum circuits on the reference coupling graphs of Processor A (5 qubits) and Processor B (9 qubits). The benchmark evaluates circuit performance using the specified basis gates, noise parameters, transpilation settings, and 4096 measurement shots.

## Important Notes

ML-KEM, ML-DSA, Falcon, and AES-GCM are classical cryptographic algorithms. They run on the host computer and are not executed as quantum circuits on Processor A or Processor B.

The Qiskit experiment evaluates a test quantum circuit on two simulated processor architectures. Cryptographic performance is measured separately using Python. The results of these experiments are reported independently.

The processor configurations use the reference coupling graph for Processor A and the specified 12-edge graph for Processor B. Both configurations use the following noise parameters:

- Single-qubit depolarizing error: 0.001
- CX gate depolarizing error: 0.005
- Readout error: 0.01

## Repository Structure

- `processors/processor_A.json` – Processor A configuration.
- `processors/processor_B.json` – Processor B configuration.
- `src/processors.py` – Loads processor graph and noise configurations.
- `src/routing.py` – Handles circuit transpilation and routing.
- `src/problem.py` – Defines the repeatable five-qubit test circuit.
- `src/metrics.py` – Calculates circuit metrics and total variation distance.
- `src/visualization.py` – Generates topology and benchmark plots.
- `main.py` – Runs the Processor A/B benchmark and exports results.
- `benchmark_crypto.py` – Benchmarks the cryptographic algorithms and secure-channel workflow.
- `algorithms/` – Contains cryptographic algorithm wrappers using `liboqs-python`.
- `encryption/aes_gcm.py` – Implements AES-256-GCM encryption.
- `tests/` – Contains tests for cryptographic functions.
- `results/tables/` – Stores generated tables and benchmark data.
- `results/figures/` – Stores generated plots and figures.

## Requirements

- Python 3.11 (recommended)
- Qiskit and the required simulation packages
- `liboqs-python` and a compatible `liboqs` native library
- The other dependencies listed in `requirements.txt`

## Installation

Open PowerShell in the project directory and run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The cryptographic wrappers require a compatible installation of `liboqs`. If the `oqs` module cannot be imported, install and configure the required native library according to the official liboqs installation instructions.

## Running the Experiments

Run the following commands in order:

```powershell
python check_environment.py
python test_ml_kem.py
python test_ml_dsa.py
python test_falcon.py
python main.py
python benchmark_crypto.py --iterations 20
```

The environment check verifies the required dependencies. The cryptographic test scripts check the individual algorithm implementations. The main benchmark evaluates the two processor configurations, while the cryptographic benchmark measures algorithm and secure-channel performance.

## Results

The processor benchmark generates circuit metrics, measurement counts, and visualizations for comparing Processor A and Processor B.

The cryptographic benchmark records execution times and summary statistics for the supported algorithms and secure-channel workflow. Results are saved as CSV, JSON, and plot files where implemented by the scripts.

## Reproducibility

- Transpilation optimization level: 1
- Transpilation seed: 42
- Quantum simulator shots: 4096
- Processor topology and noise parameters are defined in JSON configuration files.
- Cryptographic execution times are measured using Python's `time.perf_counter()`.
- Execution times depend on the host computer and software environment.
- Memory measurements using Python's `tracemalloc` represent Python-managed memory allocations and may not include all native-library memory usage.
- The SWAP metric counts explicit SWAP instructions in the transpiled circuit. Routing overhead may also appear as additional CX gates, so CX count and circuit depth should be considered when comparing results.

## Conclusion

This project provides a reproducible framework
