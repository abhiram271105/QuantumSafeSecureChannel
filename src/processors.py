import json
from pathlib import Path
from qiskit.transpiler import CouplingMap
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

ROOT = Path(__file__).resolve().parents[1]
PROCESSORS_DIR = ROOT / "processors"

def load_processor(name):
    path = PROCESSORS_DIR / f"{name}.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def get_coupling_map(name):
    cfg = load_processor(name)
    directed = []
    for a, b in cfg["edges_undirected"]:
        directed.extend([[a, b], [b, a]])
    return CouplingMap(couplinglist=directed)

def create_noise_model(name):
    cfg = load_processor(name)
    p1 = cfg["noise"]["one_qubit_depolarizing_probability"]
    pcx = cfg["noise"]["cx_depolarizing_probability"]
    pr = cfg["noise"]["readout_error_probability"]
    model = NoiseModel()
    model.add_all_qubit_quantum_error(depolarizing_error(p1, 1), ["rz", "sx", "x"])
    model.add_all_qubit_quantum_error(depolarizing_error(pcx, 2), ["cx"])
    model.add_all_qubit_readout_error(ReadoutError([[1-pr, pr], [pr, 1-pr]]))
    return model
