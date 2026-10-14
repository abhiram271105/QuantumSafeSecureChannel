from qiskit import QuantumCircuit

def create_architecture_probe():
    """A deterministic 5-logical-qubit circuit that exercises nonlocal connectivity."""
    qc = QuantumCircuit(5, 5, name="architecture_probe")
    qc.h(0)
    qc.h(2)
    qc.rz(0.37, 1)
    qc.rz(0.61, 3)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 3)
    qc.cx(3, 4)
    qc.cx(0, 4)
    qc.cx(1, 3)
    qc.cx(0, 2)
    qc.cx(2, 4)
    qc.h(0)
    qc.h(1)
    qc.measure(range(5), range(5))
    return qc
