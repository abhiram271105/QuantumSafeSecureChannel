def circuit_metrics(compiled, processor_name, logical_qubits, shots, physical_qubits):
    ops = {str(k): int(v) for k, v in compiled.count_ops().items()}
    return {
        "processor": processor_name.replace("_", " ").title(),
        "physical_qubits": int(physical_qubits),
        "logical_qubits": int(logical_qubits),
        "depth": int(compiled.depth()),
        "cx_count": int(ops.get("cx", 0)),
        "explicit_swap_count": int(ops.get("swap", 0)),
        "single_qubit_gate_count": int(sum(ops.get(g, 0) for g in ("rz", "sx", "x"))),
        "operation_counts": ops,
        "shots": int(shots),
    }

def total_variation_distance(counts_a, counts_b, shots):
    pa = {k: v / shots for k, v in counts_a.items()}
    pb = {k: v / shots for k, v in counts_b.items()}
    keys = set(pa) | set(pb)
    return 0.5 * sum(abs(pa.get(k, 0.0) - pb.get(k, 0.0)) for k in keys)
