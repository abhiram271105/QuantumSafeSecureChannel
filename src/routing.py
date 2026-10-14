from qiskit import transpile
from src.processors import load_processor, get_coupling_map

def transpile_for_processor(circuit, processor_name):
    cfg = load_processor(processor_name)
    return transpile(
        circuit,
        coupling_map=get_coupling_map(processor_name),
        basis_gates=cfg["basis_gates"],
        optimization_level=cfg["transpilation"]["optimization_level"],
        seed_transpiler=cfg["transpilation"]["seed_transpiler"],
    )
