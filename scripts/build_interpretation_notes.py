from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv


INPUT_PATH = Path("results/processed/combined_research_summary.csv")
OUTPUT_PATH = Path("results/processed/interpretation_notes.txt")


def load_rows(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        for key in ["metric_1_value", "metric_2_value", "metric_3_value", "metric_4_value"]:
            if row[key] != "":
                row[key] = float(row[key])

    return rows


def select(rows: list[dict], category: str, subject: str | None = None) -> list[dict]:
    filtered = [row for row in rows if row["category"] == category]
    if subject is not None:
        filtered = [row for row in filtered if row["subject"] == subject]
    return filtered


def format_ordered(rows: list[dict]) -> list[str]:
    ordered = sorted(rows, key=lambda x: x["metric_1_value"])
    lines = []
    for row in ordered:
        lines.append(
            f"- {row['transport']}: "
            f"{row['metric_1_name']}={row['metric_1_value']:.3f}, "
            f"{row['metric_2_name']}={row['metric_2_value']:.3f}"
        )
    return lines


def build_notes(rows: list[dict]) -> str:
    lines: list[str] = []

    lines.append("ROBOCZA INTERPRETACJA WYNIKÓW")
    lines.append("")

    lines.append("1. Scenariusz request-response")
    for operation in ["set_value", "get_value"]:
        operation_rows = select(rows, "request_response", operation)
        ordered = sorted(operation_rows, key=lambda x: x["metric_1_value"])
        best = ordered[0]
        worst = ordered[-1]

        lines.append(f"Operacja: {operation}")
        lines.extend(format_ordered(operation_rows))
        lines.append(
            f"Wstępna obserwacja: najlepszy wynik średni uzyskał transport "
            f"{best['transport']}, natomiast najsłabszy wynik średni uzyskał "
            f"{worst['transport']}."
        )
        lines.append(
            "Interpretacja robocza: różnice w tym scenariuszu wynikają głównie z "
            "charakteru transportu, kosztu opakowania komunikatu oraz sposobu "
            "realizacji wywołania żądanie-odpowiedź."
        )
        lines.append("")

    lines.append("2. Scenariusz realtime fetch")
    for scenario in ["non_empty_fetch", "empty_fetch"]:
        scenario_rows = select(rows, "realtime_fetch", scenario)
        ordered = sorted(scenario_rows, key=lambda x: x["metric_1_value"])
        best = ordered[0]
        worst = ordered[-1]

        lines.append(f"Scenariusz: {scenario}")
        lines.extend(format_ordered(scenario_rows))
        lines.append(
            f"Wstępna obserwacja: w scenariuszu {scenario} najlepszy średni czas "
            f"uzyskał transport {best['transport']}, a najwyższy {worst['transport']}."
        )
        lines.append(
            "Interpretacja robocza: ten wynik pozwala porównywać koszt pobrania zmian "
            "stanu przy różnych metodach komunikacji, w tym koszt sprawdzenia braku nowych danych."
        )
        lines.append("")

    lines.append("3. Rozmiar komunikatów i serializacja")
    for operation in ["set_value", "get_value"]:
        operation_rows = select(rows, "message_size_and_serialization", operation)
        by_size = sorted(operation_rows, key=lambda x: x["metric_1_value"])
        smallest = by_size[0]
        largest = by_size[-1]

        lines.append(f"Operacja: {operation}")
        for row in by_size:
            lines.append(
                f"- {row['transport']}: "
                f"{row['metric_1_name']}={int(row['metric_1_value'])}, "
                f"{row['metric_2_name']}={int(row['metric_2_value'])}, "
                f"{row['notes']}"
            )
        lines.append(
            f"Wstępna obserwacja: najmniejszy request dla operacji {operation} "
            f"uzyskał transport {smallest['transport']}, a największy {largest['transport']}."
        )
        lines.append(
            "Interpretacja robocza: wyniki tej części pokazują koszt reprezentacji "
            "komunikatu i wpływ formatu danych na rozmiar oraz koszt przetwarzania."
        )
        lines.append("")

    lines.append("4. Koszt walidacji")
    validation_rows = select(rows, "validation_cost")
    ordered_validation = sorted(validation_rows, key=lambda x: x["metric_1_value"])

    for row in ordered_validation:
        lines.append(
            f"- {row['subject']}: "
            f"{row['metric_1_name']}={row['metric_1_value']:.3f}, "
            f"{row['metric_2_name']}={row['metric_2_value']:.3f}, "
            f"{row['notes']}"
        )

    lines.append(
        "Wstępna obserwacja: baseline bez walidacji stanowi punkt odniesienia, "
        "na tle którego można oceniać narzut walidacji strukturalnej oraz biznesowej."
    )
    lines.append(
        "Interpretacja robocza: walidacja zwiększa koszt pojedynczego przetwarzania, "
        "ale jednocześnie poprawia kontrolę poprawności danych i umożliwia odrzucenie "
        "niepoprawnych komunikatów na odpowiednim etapie."
    )
    lines.append("")

    lines.append("5. Syntetyczne wnioski robocze")
    lines.append(
        "- Badane metody komunikacji różnią się nie tylko czasem wykonania operacji, "
        "ale również kosztem reprezentacji komunikatu."
    )
    lines.append(
        "- Format protobuf może dawać przewagę rozmiarową względem JSON, co może "
        "przekładać się na mniejszy koszt komunikacji."
    )
    lines.append(
        "- Utrzymywane połączenie może być korzystne w scenariuszach częstego pobierania "
        "zmian lub komunikacji zbliżonej do czasu rzeczywistego."
    )
    lines.append(
        "- Walidacja danych stanowi dodatkowy koszt wykonania, ale pełni istotną rolę "
        "w zapewnieniu poprawności i odporności systemu."
    )
    lines.append(
        "- Dobór metody komunikacji powinien zależeć od charakteru scenariusza: "
        "proste request-response, częste pobieranie zmian, wymagania dotyczące "
        "rozmiaru komunikatów oraz oczekiwany poziom kontroli poprawności danych."
    )

    return "\n".join(lines)


def main() -> None:
    rows = load_rows(INPUT_PATH)
    notes = build_notes(rows)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        f.write(notes)

    print(f"Interpretation notes saved to: {OUTPUT_PATH}")
    print()
    print(notes)


if __name__ == "__main__":
    main()