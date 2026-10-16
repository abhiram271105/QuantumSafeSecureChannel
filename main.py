import csv
import json
from pathlib import Path

from qiskit_aer import AerSimulator

from src.problem import create_architecture_probe
from src.processors import load_processor, create_noise_model
from src.routing import transpile_for_processor
from src.metrics import circuit_metrics, total_variation_distance
from src.visualization import (
    plot_topologies,
    plot_processor_comparison,
    plot_four_case_comparison,
)

ROOT = Path(__file__).resolve().parent

TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"

TABLES.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

def run_processor(processor_name, logical_circuit, case_ideal, case_noisy):

    config = load_processor(processor_name)
    shots = config["transpilation"]["shots"]

    compiled = transpile_for_processor(
        logical_circuit,
        processor_name,
    )
    metrics = circuit_metrics(
        compiled,
        processor_name,
        logical_circuit.num_qubits,
        shots,
        config["num_qubits"],
    )


    ideal_backend = AerSimulator()

    ideal_result = ideal_backend.run(
        compiled,
        shots=shots,
        seed_simulator=42,
    ).result()

    ideal_counts = ideal_result.get_counts()

    noisy_backend = AerSimulator(
        noise_model=create_noise_model(processor_name),
    )

    noisy_result = noisy_backend.run(
        compiled,
        shots=shots,
        seed_simulator=42,
    ).result()

    noisy_counts = noisy_result.get_counts()



    tvd = round(
        total_variation_distance(
            ideal_counts,
            noisy_counts,
            shots,
        ),
        8,
    )


    common = {
        "processor": metrics["processor"],
        "physical_qubits": metrics["physical_qubits"],
        "logical_qubits": metrics["logical_qubits"],
        "depth": metrics["depth"],
        "cx_count": metrics["cx_count"],
        "explicit_swap_count": metrics["explicit_swap_count"],
        "single_qubit_gate_count": metrics["single_qubit_gate_count"],
        "shots": shots,
        "tvd_ideal_vs_noisy": tvd,
        "simulation_mode": (
            "Qiskit Aer; synthetic noise from processor JSON"
        ),
    }



    ideal_row = {
        **common,
        "case": case_ideal,
        "simulation_type": "Ideal",
        "counts": ideal_counts,
        "distinct_outcomes": len(ideal_counts),
        "total_measurement_shots": sum(ideal_counts.values()),
    }



    noisy_row = {
        **common,
        "case": case_noisy,
        "simulation_type": "Noisy",
        "counts": noisy_counts,
        "distinct_outcomes": len(noisy_counts),
        "total_measurement_shots": sum(noisy_counts.values()),
    }

    return ideal_row, noisy_row, compiled




def save_results(rows):



    json_path = TABLES / "processor_ab_metrics.json"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(rows, file, indent=2)



    csv_path = TABLES / "processor_ab_metrics.csv"

    scalar_fields = [
        "case",
        "processor",
        "simulation_type",
        "physical_qubits",
        "logical_qubits",
        "depth",
        "cx_count",
        "explicit_swap_count",
        "single_qubit_gate_count",
        "shots",
        "total_measurement_shots",
        "distinct_outcomes",
        "tvd_ideal_vs_noisy",
        "simulation_mode",
    ]

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=scalar_fields,
        )

        writer.writeheader()

        for row in rows:
            writer.writerow({
                field: row.get(field)
                for field in scalar_fields
            })



    comparison_path = TABLES / "processor_tvd_comparison.csv"

    comparison_fields = [
        "processor",
        "ideal_case",
        "noisy_case",
        "ideal_shots",
        "noisy_shots",
        "ideal_distinct_outcomes",
        "noisy_distinct_outcomes",
        "tvd_ideal_vs_noisy",
    ]

    comparisons = []

    for processor_name, ideal_case, noisy_case in [
        ("Processor A", "A1", "A2"),
        ("Processor B", "B1", "B2"),
    ]:

        ideal_row = next(
            row for row in rows
            if row["case"] == ideal_case
        )

        noisy_row = next(
            row for row in rows
            if row["case"] == noisy_case
        )


        verified_tvd = round(
            total_variation_distance(
                ideal_row["counts"],
                noisy_row["counts"],
                ideal_row["shots"],
            ),
            8,
        )

        comparisons.append({
            "processor": processor_name,
            "ideal_case": ideal_case,
            "noisy_case": noisy_case,
            "ideal_shots": ideal_row["shots"],
            "noisy_shots": noisy_row["shots"],
            "ideal_distinct_outcomes": ideal_row["distinct_outcomes"],
            "noisy_distinct_outcomes": noisy_row["distinct_outcomes"],
            "tvd_ideal_vs_noisy": verified_tvd,
        })

    with comparison_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=comparison_fields,
        )

        writer.writeheader()
        writer.writerows(comparisons)


    comparison_json_path = TABLES / "processor_tvd_comparison.json"

    with comparison_json_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(comparisons, file, indent=2)

    print("\nRESULT FILES SAVED")
    print("-" * 60)
    print("Four-case CSV:", csv_path)
    print("Four-case JSON:", json_path)
    print("TVD comparison CSV:", comparison_path)
    print("TVD comparison JSON:", comparison_json_path)




def print_results(rows):

    print("\n" + "=" * 100)
    print("QFF 2026 - PROCESSOR A/B FOUR-CASE RESULTS")
    print("=" * 100)

    headers = [
        "Case",
        "Processor",
        "Type",
        "Qubits",
        "Depth",
        "CX",
        "SWAP",
        "Shots",
        "Outcomes",
    ]

    print(
        f"{headers[0]:<8}"
        f"{headers[1]:<18}"
        f"{headers[2]:<10}"
        f"{headers[3]:<9}"
        f"{headers[4]:<9}"
        f"{headers[5]:<7}"
        f"{headers[6]:<8}"
        f"{headers[7]:<9}"
        f"{headers[8]:<10}"
    )

    print("-" * 100)

    for row in rows:

        print(
            f"{row['case']:<8}"
            f"{row['processor']:<18}"
            f"{row['simulation_type']:<10}"
            f"{row['physical_qubits']:<9}"
            f"{row['depth']:<9}"
            f"{row['cx_count']:<7}"
            f"{row['explicit_swap_count']:<8}"
            f"{row['shots']:<9}"
            f"{row['distinct_outcomes']:<10}"
        )

    print("\nIDEAL-VERSUS-NOISY TVD")
    print("-" * 45)

    for ideal_case, noisy_case in [
        ("A1", "A2"),
        ("B1", "B2"),
    ]:

        ideal_row = next(
            row for row in rows
            if row["case"] == ideal_case
        )

        noisy_row = next(
            row for row in rows
            if row["case"] == noisy_case
        )

        tvd = total_variation_distance(
            ideal_row["counts"],
            noisy_row["counts"],
            ideal_row["shots"],
        )

        print(
            f"{ideal_row['processor']}: "
            f"{ideal_case} vs {noisy_case} = {tvd:.8f}"
        )




def main():

    print("=" * 68)
    print("QFF 2026 - Quantum Processor Architecture Benchmark")
    print("=" * 68)

    print("\nCreating architecture probe circuit...")

    logical_circuit = create_architecture_probe()

    rows = []

    processors = [
        ("processor_A", "A1", "A2"),
        ("processor_B", "B1", "B2"),
    ]



    for processor_name, ideal_case, noisy_case in processors:

        print("\n" + "-" * 60)
        print("Running:", processor_name)
        print("-" * 60)

        ideal_row, noisy_row, compiled = run_processor(
            processor_name,
            logical_circuit,
            ideal_case,
            noisy_case,
        )

        rows.append(ideal_row)
        rows.append(noisy_row)

        circuit_path = TABLES / f"{processor_name}_compiled.txt"

        circuit_path.write_text(
            str(compiled.draw(output="text")),
            encoding="utf-8",
        )

        print("Compiled circuit saved:", circuit_path)
        print(f"{ideal_case}: ideal simulation completed")
        print(f"{noisy_case}: noisy simulation completed")



    save_results(rows)
    print_results(rows)



    print("\nGenerating figures...")


    plot_topologies()


    processor_rows = [
        next(row for row in rows if row["case"] == "A1"),
        next(row for row in rows if row["case"] == "B1"),
    ]

    plot_processor_comparison(processor_rows)


    plot_four_case_comparison(rows)



    print("\n" + "=" * 68)
    print("SIMULATION COMPLETED SUCCESSFULLY")
    print("=" * 68)

    print("\nFour cases generated:")
    print("A1 - Processor A ideal")
    print("A2 - Processor A noisy")
    print("B1 - Processor B ideal")
    print("B2 - Processor B noisy")

    print("\nTables directory:")
    print(TABLES)

    print("\nFigures directory:")
    print(FIGURES)

    print("\nNote:")
    print(
        "These results use Qiskit Aer and synthetic noise models. "
        "They are simulations, not measurements from physical hardware."
    )


if __name__ == "__main__":
    main()