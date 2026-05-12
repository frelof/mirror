#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import math
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


def parse_timestamp(value: str) -> dt.datetime:
    cleaned = value.strip().strip('"')
    if cleaned.endswith("Z"):
        cleaned = f"{cleaned[:-1]}+00:00"
    return dt.datetime.fromisoformat(cleaned)


def parse_float(value: str):
    cleaned = value.strip()
    if cleaned == "":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def load_daily_averages(path: Path):
    aggregates = defaultdict(lambda: {"temp_sum": 0.0, "temp_count": 0, "hum_sum": 0.0, "hum_count": 0})

    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            ts = row.get("timestamp", "").strip()
            if not ts:
                continue
            try:
                day = parse_timestamp(ts).date()
            except ValueError:
                continue

            temp = parse_float(row.get("temperature_c", ""))
            if temp is not None:
                aggregates[day]["temp_sum"] += temp
                aggregates[day]["temp_count"] += 1

            humidity = parse_float(row.get("humidity_percent", ""))
            if humidity is not None:
                aggregates[day]["hum_sum"] += humidity
                aggregates[day]["hum_count"] += 1

    days = sorted(aggregates.keys())
    temps = []
    hums = []
    for day in days:
        record = aggregates[day]
        if record["temp_count"]:
            temps.append(record["temp_sum"] / record["temp_count"])
        else:
            temps.append(math.nan)
        if record["hum_count"]:
            hums.append(record["hum_sum"] / record["hum_count"])
        else:
            hums.append(math.nan)

    return days, temps, hums


def plot_daily_averages(days, temps, hums, output_path: Path):
    fig, ax_temp = plt.subplots(figsize=(10, 5))
    ax_temp.plot(days, temps, color="#2c6e9b", label="Avg temp (C)")
    ax_temp.set_xlabel("Date")
    ax_temp.set_ylabel("Temperature (C)", color="#2c6e9b")
    ax_temp.tick_params(axis="y", labelcolor="#2c6e9b")

    ax_hum = ax_temp.twinx()
    ax_hum.plot(days, hums, color="#cf6b3f", label="Avg humidity (%)")
    ax_hum.set_ylabel("Humidity (%)", color="#cf6b3f")
    ax_hum.tick_params(axis="y", labelcolor="#cf6b3f")

    fig.suptitle("Daily Averages")
    fig.autofmt_xdate()

    lines, labels = ax_temp.get_legend_handles_labels()
    lines2, labels2 = ax_hum.get_legend_handles_labels()
    ax_temp.legend(lines + lines2, labels + labels2, loc="upper left")

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)


def resolve_default_input():
    script_dir = Path(__file__).parent
    utils_path = script_dir / "readings.csv"
    if utils_path.exists():
        return utils_path
    # Fallback to project root
    project_root = script_dir.parent
    return project_root / "readings.csv"


def main():
    script_dir = Path(__file__).parent
    parser = argparse.ArgumentParser(description="Compute daily averages and plot temperature/humidity.")
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=resolve_default_input(),
        help="Input CSV with timestamp, temperature_c, humidity_percent columns.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=script_dir / "daily_averages.png",
        help="Output PNG path.",
    )
    args = parser.parse_args()

    days, temps, hums = load_daily_averages(args.input)
    if not days:
        raise SystemExit(f"No data found in {args.input}")

    plot_daily_averages(days, temps, hums, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
