import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from src.processors import load_processor


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "results" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)


def plot_topologies():
    """Save the physical connectivity graph for each processor."""

    for name in ("processor_A", "processor_B"):
        cfg = load_processor(name)

        graph = nx.Graph()
        graph.add_nodes_from(range(cfg["num_qubits"]))
        graph.add_edges_from(cfg["edges_undirected"])

        pos = nx.spring_layout(graph, seed=42)

        plt.figure(figsize=(7, 5))
        nx.draw_networkx(
            graph,
            pos=pos,
            with_labels=True,
            node_size=850,
            font_size=10,
            width=2,
        )

        plt.title(f'{cfg["name"]}: {cfg["num_qubits"]} qubits')
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(FIGURES / f"{name}_topology.png", dpi=180)
        plt.close()


def plot_processor_comparison(rows):
    """
    Generate architecture comparison charts using one ideal row
    per processor. The TVD chart compares Processor A and B.
    """

    if not rows:
        return

    labels = [row["processor"] for row in rows]

    metrics = [
        ("depth", "Compiled Circuit Depth", "depth_comparison.png"),
        ("cx_count", "Compiled CX Gate Count", "cx_comparison.png"),
        (
            "explicit_swap_count",
            "Explicit SWAP Gate Count",
            "swap_comparison.png",
        ),
        (
            "tvd_ideal_vs_noisy",
            "Ideal-versus-Noisy TVD",
            "noise_tvd_comparison.png",
        ),
    ]

    for key, title, filename in metrics:
        values = [float(row.get(key, 0)) for row in rows]

        plt.figure(figsize=(8, 5))
        plt.bar(labels, values)
        plt.ylabel(key.replace("_", " ").title())
        plt.title(title)
        plt.tight_layout()
        plt.savefig(FIGURES / filename, dpi=180)
        plt.close()


def plot_four_case_comparison(rows):
    """Generate charts that explicitly display A1, A2, B1, and B2."""

    if not rows:
        return

    labels = [row["case"] for row in rows]

    # Architecture metrics are identical between ideal and noisy
    # executions of the same compiled circuit.
    architecture_metrics = [
        ("depth", "Circuit Depth by Case", "four_case_depth.png"),
        ("cx_count", "CX Gates by Case", "four_case_cx.png"),
        (
            "explicit_swap_count",
            "Explicit SWAP Gates by Case",
            "four_case_swaps.png",
        ),
    ]

    for key, title, filename in architecture_metrics:
        values = [int(row.get(key, 0)) for row in rows]

        plt.figure(figsize=(8, 5))
        plt.bar(labels, values)
        plt.xlabel("Simulation Case")
        plt.ylabel(key.replace("_", " ").title())
        plt.title(title)
        plt.tight_layout()
        plt.savefig(FIGURES / filename, dpi=180)
        plt.close()

    # TVD is a pairwise ideal-versus-noisy metric, not an
    # independent metric for each individual case.
    pair_labels = ["Processor A (A1 vs A2)", "Processor B (B1 vs B2)"]
    pair_values = []

    for ideal_case, noisy_case in (("A1", "A2"), ("B1", "B2")):
        ideal_row = next(
            (row for row in rows if row["case"] == ideal_case), None
        )
        noisy_row = next(
            (row for row in rows if row["case"] == noisy_case), None
        )

        if ideal_row is None or noisy_row is None:
            continue

        pair_values.append(
            float(ideal_row["tvd_ideal_vs_noisy"])
        )

    if len(pair_values) == 2:
        plt.figure(figsize=(8, 5))
        plt.bar(pair_labels, pair_values)
        plt.ylabel("Total Variation Distance")
        plt.title("Ideal-versus-Noisy Distribution Difference")
        plt.tight_layout()
        plt.savefig(FIGURES / "ideal_noisy_tvd.png", dpi=180)
        plt.close()

    # Plot the number of distinct measurement outcomes.
    outcome_counts = [
        len(row.get("counts", {}))
        for row in rows
    ]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, outcome_counts)
    plt.xlabel("Simulation Case")
    plt.ylabel("Distinct Measurement Outcomes")
    plt.title("Measurement Outcome Diversity")
    plt.tight_layout()
    plt.savefig(FIGURES / "four_case_outcomes.png", dpi=180)
    plt.close()


def plot_crypto_summary(csv_rows):
    """Plot cryptographic operation timings when benchmark data exists."""

    if not csv_rows:
        return

    labels = [row["algorithm"] for row in csv_rows]
    values = [
        float(row["median_operation_ms"])
        for row in csv_rows
    ]

    plt.figure(figsize=(9, 5))
    plt.bar(labels, values)
    plt.ylabel("Median Operation Time (ms)")
    plt.title("Cryptographic Operation Benchmark (Host CPU)")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(FIGURES / "crypto_operation_time.png", dpi=180)
    plt.close()