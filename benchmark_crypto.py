import argparse, csv, json, statistics, time, tracemalloc, platform, os
from pathlib import Path
from algorithms.kem.ml_kem import MLKEM
from algorithms.signature.ml_dsa import MLDSA
from algorithms.signature.falcon import Falcon
from encryption.aes_gcm import AesGcmEncryption
from cryptography.exceptions import InvalidTag
from src.visualization import plot_crypto_summary

ROOT = Path(__file__).resolve().parent
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"
TABLES.mkdir(parents=True, exist_ok=True)

def timed(fn):
    start = time.perf_counter()
    result = fn()
    return (time.perf_counter() - start) * 1000.0, result

def measure_peak_python_memory(fn):
    tracemalloc.start()
    try:
        result = fn()
        _, peak = tracemalloc.get_traced_memory()
        return result, peak
    finally:
        tracemalloc.stop()

def benchmark_kem(iterations, message):
    rows = []
    for i in range(iterations):
        kem = MLKEM("ML-KEM-768")
        try:
            ms_keygen, public_key = timed(kem.generate_keypair)
            ms_encap, pair = timed(lambda: kem.encapsulate(public_key))
            ciphertext, sender_secret = pair
            ms_decap, receiver_secret = timed(lambda: kem.decapsulate(ciphertext))
            if sender_secret != receiver_secret:
                raise RuntimeError("ML-KEM sender/receiver shared secrets differ")
            rows.append({
                "iteration": i + 1, "algorithm": "ML-KEM-768",
                "operation": "keygen+encap+decap",
                "keygen_ms": ms_keygen, "encapsulation_ms": ms_encap,
                "decapsulation_ms": ms_decap, "signing_ms": "",
                "verification_ms": "", "public_key_bytes": len(public_key),
                "ciphertext_bytes": len(ciphertext), "signature_bytes": "",
                "success": True
            })
        finally:
            kem.close()
    return rows

def benchmark_signature(algorithm, cls, iterations, message):
    rows = []
    for i in range(iterations):
        signer = cls(algorithm)
        try:
            ms_keygen, public_key = timed(signer.generate_keypair)
            ms_sign, signature = timed(lambda: signer.sign_message(message))
            ms_verify, valid = timed(lambda: signer.verify_signature(message, signature, public_key))
            altered_valid = signer.verify_signature(message + " [tampered]", signature, public_key)
            if not valid or altered_valid:
                raise RuntimeError(f"{algorithm}: signature validity/tamper check failed")
            rows.append({
                "iteration": i + 1, "algorithm": algorithm,
                "operation": "keygen+sign+verify",
                "keygen_ms": ms_keygen, "encapsulation_ms": "",
                "decapsulation_ms": "", "signing_ms": ms_sign,
                "verification_ms": ms_verify, "public_key_bytes": len(public_key),
                "ciphertext_bytes": "", "signature_bytes": len(signature),
                "success": True
            })
        finally:
            signer.close()
    return rows

def benchmark_secure_channel(iterations, message):
    rows = []
    for i in range(iterations):
        bob = MLKEM("ML-KEM-768")
        alice = MLKEM("ML-KEM-768")
        try:
            pk = bob.generate_keypair()
            ciphertext, secret_a = alice.encapsulate(pk)
            secret_b = bob.decapsulate(ciphertext)
            if secret_a != secret_b:
                raise RuntimeError("Shared secret mismatch")
            aes_a = AesGcmEncryption(secret_a)
            aes_b = AesGcmEncryption(secret_b)
            ms_encrypt, encrypted = timed(lambda: aes_a.encrypt(message))
            nonce, payload = encrypted
            ms_decrypt, plaintext = timed(lambda: aes_b.decrypt(nonce, payload))
            if plaintext != message:
                raise RuntimeError("Decrypted message mismatch")
            tampered = bytearray(payload)
            tampered[0] ^= 1
            tamper_rejected = False
            try:
                aes_b.decrypt(nonce, bytes(tampered))
            except (InvalidTag, ValueError):
                tamper_rejected = True
            if not tamper_rejected:
                raise RuntimeError("AES-GCM tampering test failed")
            rows.append({
                "iteration": i + 1, "algorithm": "ML-KEM-768 + AES-256-GCM",
                "operation": "secure-channel",
                "keygen_ms": "", "encapsulation_ms": "", "decapsulation_ms": "",
                "signing_ms": "", "verification_ms": "",
                "public_key_bytes": len(pk), "ciphertext_bytes": len(ciphertext),
                "signature_bytes": "", "encryption_ms": ms_encrypt,
                "decryption_ms": ms_decrypt, "message_bytes": len(message.encode("utf-8")),
                "tamper_rejected": tamper_rejected, "success": True
            })
        finally:
            alice.close()
            bob.close()
    return rows

def median_num(rows, key):
    vals = [float(r[key]) for r in rows if r.get(key) not in ("", None)]
    return statistics.median(vals) if vals else ""

def main():
    parser = argparse.ArgumentParser(description="Benchmark PQC algorithms on the host CPU.")
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--message", default="QFF 2026 quantum-safe secure channel benchmark message.")
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error("--iterations must be at least 1")
    message = args.message

    print("PQC benchmark on current host (not a quantum processor run)")
    print("Host:", platform.platform())
    print("Iterations per algorithm:", args.iterations)
    all_rows = []
    all_rows += benchmark_kem(args.iterations, message)
    all_rows += benchmark_signature("ML-DSA-65", MLDSA, args.iterations, message)
    all_rows += benchmark_signature("Falcon-512", Falcon, args.iterations, message)
    all_rows += benchmark_secure_channel(args.iterations, message)

    raw_path = TABLES / "crypto_benchmark_raw.csv"
    fieldnames = sorted(set().union(*(r.keys() for r in all_rows)))
    with raw_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    summaries = []
    for alg in ("ML-KEM-768", "ML-DSA-65", "Falcon-512", "ML-KEM-768 + AES-256-GCM"):
        subset = [r for r in all_rows if r["algorithm"] == alg]
        if not subset:
            continue
        summaries.append({
            "algorithm": alg,
            "iterations": len(subset),
            "median_keygen_ms": median_num(subset, "keygen_ms"),
            "median_encapsulation_ms": median_num(subset, "encapsulation_ms"),
            "median_decapsulation_ms": median_num(subset, "decapsulation_ms"),
            "median_signing_ms": median_num(subset, "signing_ms"),
            "median_verification_ms": median_num(subset, "verification_ms"),
            "median_encryption_ms": median_num(subset, "encryption_ms"),
            "median_decryption_ms": median_num(subset, "decryption_ms"),
            "public_key_bytes": next((r["public_key_bytes"] for r in subset if r.get("public_key_bytes") not in ("", None)), ""),
            "ciphertext_bytes": next((r["ciphertext_bytes"] for r in subset if r.get("ciphertext_bytes") not in ("", None)), ""),
            "signature_bytes": next((r["signature_bytes"] for r in subset if r.get("signature_bytes") not in ("", None)), ""),
            "all_success": all(bool(r["success"]) for r in subset)
        })
    (TABLES / "crypto_benchmark_summary.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    with (TABLES / "crypto_benchmark_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0].keys()))
        writer.writeheader()
        writer.writerows(summaries)
    plot_crypto_summary([{
        "algorithm": s["algorithm"],
        "median_operation_ms": max([float(s[k]) for k in ("median_keygen_ms","median_encapsulation_ms","median_decapsulation_ms","median_signing_ms","median_verification_ms","median_encryption_ms","median_decryption_ms") if s[k] not in ("", None)] or [0])
    } for s in summaries])
    meta = {
        "host_platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count_logical": os.cpu_count(),
        "iterations": args.iterations,
        "message_bytes": len(message.encode("utf-8")),
        "measurement_note": "Host CPU benchmark. Does not claim execution on physical quantum hardware or on a separate constrained device."
    }
    (TABLES / "crypto_benchmark_environment.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("All correctness checks passed.")
    print("Saved:", raw_path)
    print("Saved results/tables/crypto_benchmark_summary.csv and .json")
    print("Saved results/figures/crypto_operation_time.png")

if __name__ == "__main__":
    main()
