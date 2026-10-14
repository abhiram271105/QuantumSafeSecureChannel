# Processor A/B and PQC Benchmark Report

## Problem focus
The cryptographic software component uses ML-KEM-768 for key establishment, ML-DSA-65 and Falcon-512 for digital signatures, and AES-256-GCM for authenticated message encryption.

## Processor architecture experiment
Processor A is modeled as a 5-qubit branching tree with edges `(0,1), (1,2), (1,3), (3,4)`. Processor B is modeled as a 9-qubit sparse graph with the 12 reference edges recorded in `processors/processor_B.json`. Both use `{rz, sx, x, cx}`, optimization level 1, transpiler seed 42, and 4096 shots. The same synthetic noise rates are used for both graphs.

Run `python main.py`. The measured metrics are written to `results/tables/processor_ab_metrics.csv` and `.json`; topology and comparison charts are written to `results/figures/`.

## Cryptographic software experiment
Run `python benchmark_crypto.py --iterations 20`. The benchmark measures ML-KEM-768 key generation/encapsulation/decapsulation, ML-DSA-65 and Falcon-512 key generation/signing/verification, plus ML-KEM-768 + AES-256-GCM secure-channel operations. Correctness checks include matching shared secrets, valid signatures, rejection of altered messages, successful decryption, and rejection of modified ciphertexts.

## How to interpret the two experiments
The Qiskit circuit benchmark measures how connectivity affects compilation and noisy output distributions for a separate test circuit. It does not execute ML-KEM, ML-DSA, or Falcon on qubits. The cryptographic benchmark measures native classical cryptographic software on the host computer. Timing results are machine- and library-dependent.

## Results
Populate this section after running both scripts. Do not copy illustrative numbers from other machines. Discuss the actual measured circuit depth, CX count, explicit SWAP count, ideal/noisy distribution distance, crypto timings, and object sizes exported by the scripts.

## Limitations
- Aer is a simulator, not a physical QPU.
- The noise model is synthetic and uniform, as specified by the challenge guide.
- Explicit SWAP count can be zero even when routing cost appears as extra CX gates.
- `tracemalloc` measures Python-managed allocations and may not capture native library allocations.
- Crypto timings are from the host CPU and must not be labeled as Processor A/B qubit execution.
