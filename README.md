# QuantumSafeSecureChannel

## QFF 2026 — Phase 1

**Problem Statement:** Quantum-Safe Secure Channel in Cryptography  
**Track:** Post-Quantum Cryptography

## 1. Project Overview

QuantumSafeSecureChannel is a prototype for secure messaging using post-quantum cryptography. It combines post-quantum key establishment, digital signatures, key derivation, and authenticated encryption to demonstrate how a quantum-safe communication channel can be built.

The application uses ML-KEM to establish a shared secret, ML-DSA or Falcon for digital signatures, HKDF to derive an encryption key, and AES-256-GCM to protect messages.

The repository also contains a separate Qiskit experiment that compares simulated quantum processor architectures. This experiment is independent of the classical cryptographic application; the cryptographic algorithms do not execute on quantum processors.

## 2. Objectives

- Demonstrate post-quantum key establishment using ML-KEM.
- Sign and verify transmitted message packages using post-quantum digital signatures.
- Derive symmetric encryption keys using HKDF.
- Encrypt and decrypt messages using AES-256-GCM.
- Detect modified messages and reject invalid signatures.
- Measure cryptographic operation times and record benchmark results.
- Identify the performance and implementation requirements for deployment on resource-constrained platforms.

## 3. Cryptographic Components

| Component | Algorithms | Purpose |
|---|---|---|
| Key establishment | ML-KEM-512, ML-KEM-768, ML-KEM-1024 | Establish a shared secret |
| Digital signatures | ML-DSA-44, ML-DSA-65, ML-DSA-87, Falcon-512, Falcon-1024 | Sign and verify message packages |
| Key derivation | HKDF with SHA-256 | Derive a 256-bit encryption key |
| Symmetric encryption | AES-256-GCM | Encrypt messages and detect ciphertext modification |

The application uses `liboqs-python` for post-quantum cryptographic operations and the Python `cryptography` library for key derivation and authenticated encryption.

## 4. How the Secure Channel Works

1. The recipient generates an ML-KEM key pair.
2. The sender uses the recipient's public key to encapsulate a shared secret.
3. HKDF derives a 256-bit AES encryption key from the shared secret.
4. AES-256-GCM encrypts the message and provides ciphertext integrity protection.
5. The sender signs the message package using the selected digital signature algorithm.
6. The receiver verifies the signature before accepting the package.
7. The receiver decapsulates the ML-KEM ciphertext, derives the encryption key, and decrypts the message.
8. Invalid signatures or modified ciphertexts should result in rejection.

The current application demonstrates these operations in a local prototype. Securely associating public keys with verified identities is necessary before this design can be considered resistant to real-world impersonation or man-in-the-middle attacks.

## 5. Man-in-the-Middle Threat

A man-in-the-middle attacker may intercept communication, replace exchanged data, or impersonate a communicating party.

ML-KEM establishes a shared secret but does not authenticate the identity of the other party on its own. Digital signatures can help authenticate communication when the verification key is securely bound to the intended identity and the signed data includes the relevant handshake and session context.

The prototype signs the transmitted package and checks the signature before decryption. However, its current key handling is local to the application. A production implementation would also require a secure public-key trust mechanism, robust session binding, replay protection, and appropriate key lifecycle management.

## 6. Application and Repository Structure

```text
QuantumSafeSecureChannel/
├── algorithms/
│   ├── kem/
│   │   └── ml_kem.py
│   └── signature/
│       ├── ml_dsa.py
│       └── falcon.py
├── encryption/
│   └── aes_gcm.py
├── processors/
│   ├── processor_A.json
│   └── processor_B.json
├── src/
│   ├── metrics.py
│   ├── problem.py
│   ├── processors.py
│   ├── routing.py
│   └── visualization.py
├── tests/
│   └── test_crypto.py
├── results/
│   ├── figures/
│   └── tables/
├── app.py
├── main.py
├── benchmark_crypto.py
├── check_environment.py
├── requirements.txt
└── README.md
```

### Main files

- `app.py` — Streamlit interface for secure messaging and processor results.
- `benchmark_crypto.py` — Measures cryptographic operation times and performs correctness checks.
- `main.py` — Runs the separate Qiskit processor architecture simulation.
- `check_environment.py` — Checks whether the required Python modules can be imported.
- `tests/test_crypto.py` — Tests ML-KEM shared-secret agreement and digital signature verification.
- `results/tables/` — Contains saved benchmark tables and environment information.
- `results/figures/` — Contains generated benchmark and processor comparison figures.

## 7. Requirements

- Python 3.11 recommended
- Qiskit and Qiskit Aer
- `liboqs-python` with a compatible native `liboqs` installation
- `cryptography`
- NumPy, Matplotlib, NetworkX, and the packages listed in `requirements.txt`
- Streamlit
- Pytest

## 8. Installation

Open PowerShell in the project directory.

Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Make sure the native `liboqs` library is installed and configured correctly. The Python package alone may not be sufficient on every system.

Check the environment:

```powershell
python check_environment.py
```

Run the available cryptographic tests:

```powershell
python -m pytest tests/
```

## 9. Running the Application

Start the secure messaging interface:

```powershell
streamlit run app.py
```

The interface allows users to select supported key-establishment and signature algorithms and test the secure messaging workflow.

## 10. Running the Benchmarks

### Cryptographic benchmark

Run:

```powershell
python benchmark_crypto.py --iterations 20
```

The benchmark measures ML-KEM key generation, encapsulation and decapsulation; ML-DSA and Falcon key generation, signing and verification; and ML-KEM with AES-256-GCM for the tested secure-channel operations.

It also checks shared-secret agreement, signature validity, modified-message rejection, successful decryption, and rejection of modified ciphertexts.

The results are saved in `results/tables/`, with a summary plot in `results/figures/`.

### Separate quantum processor simulation

Run:

```powershell
python main.py
```

This experiment uses Qiskit Aer to simulate a test circuit on the configured Processor A and Processor B topologies. It compares circuit metrics and ideal versus noisy simulation results.

**Important:** These processor names refer to simulated quantum circuit architectures. They are not the hackathon's classical computing Platforms A, B, C, and custom D. This experiment does not execute ML-KEM, ML-DSA, or Falcon on quantum hardware.

## 11. Existing Cryptographic Benchmark Results

The repository contains saved results from 20 iterations on the recorded Windows host using Python 3.11.3. The benchmark message was 55 bytes.

| Algorithm | Median operation time |
|---|---:|
| ML-KEM-768 key generation | 0.295 ms |
| ML-KEM-768 encapsulation | 0.339 ms |
| ML-KEM-768 decapsulation | 0.414 ms |
| ML-DSA-65 signing | 2.742 ms |
| ML-DSA-65 verification | 0.968 ms |
| Falcon-512 signing | 6.552 ms |
| Falcon-512 verification | 0.351 ms |
| AES-256-GCM encryption | 0.0039 ms |
| AES-256-GCM decryption | 0.0025 ms |

These are existing measurements from the saved benchmark files, not guaranteed performance figures for other computers. They do not represent a complete authenticated handshake benchmark or measurements on the hackathon's Platforms A, B, C, and D.

## 12. Remaining Work for Hackathon Alignment

The current repository provides a foundation, but the following items still need to be completed or verified against the challenge requirements:

- Benchmark the complete authenticated handshake using ML-KEM, ML-DSA, HKDF, and AES-256-GCM.
- Evaluate payload sizes of approximately 1 KB, 100 KB, and 10 MB.
- Measure peak memory usage, code size, and total handshake communication overhead.
- Run reproducible tests on the required computing Platforms A, B, and C.
- Define and justify a custom Platform D configuration and benchmark it.
- Record a handshake flow diagram that matches the implemented protocol.
- Improve identity verification and session security before claiming protection against real-world man-in-the-middle attacks.

Only report measurements after running the relevant tests on the specified platform. Clearly identify any platform that has not yet been tested.

## 13. Limitations

- The secure messaging implementation is a prototype, not a production-ready communication system.
- Current cryptographic benchmark results are from the host computer.
- Python memory tracking, where used, may not capture allocations made inside native libraries.
- Qiskit Aer results are simulations based on the configured topology and synthetic noise model, not measurements from physical quantum processors.
- The saved processor simulation results and the cryptographic software results represent separate experiments.

## 14. Conclusion

QuantumSafeSecureChannel demonstrates the main building blocks of post-quantum secure messaging: key establishment, digital signatures, key derivation, and authenticated encryption. The repository includes a Streamlit application, cryptographic correctness tests, and a benchmarking framework.

Further work is needed to complete the required cross-platform evaluation, measure the full authenticated handshake, and strengthen identity and session security. These steps will help establish the practical performance and security characteristics of the proposed quantum-safe communication system.

