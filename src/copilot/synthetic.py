"""Generate deterministic fictional loans and coherent weekly collection records."""

import argparse
import hashlib
import json
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import yaml


@dataclass(frozen=True)
class SimulationConfig:
    """Validated simulation parameters; amounts are integer minor units."""

    seed: int
    as_of_date: date
    loan_count: int
    weeks: int
    principal_min_minor: int
    principal_max_minor: int
    segments: tuple[str, ...]
    channels: tuple[str, ...]
    buckets: tuple[tuple[str, int, int | None], ...]
    company: str = "XYZ Finance"
    timezone: str = "Asia/Kolkata"
    output_dir: str = "data/generated"
    currency: str = "INR"
    minor_units_per_major: int = 100

    def __post_init__(self) -> None:
        """Reject invalid bounds and overlapping or incomplete DPD buckets."""
        if not 1 <= self.loan_count <= 100_000 or not 1 <= self.weeks <= 104:
            raise ValueError("loan_count or weeks outside supported bounds")
        if not 0 < self.principal_min_minor <= self.principal_max_minor:
            raise ValueError("invalid principal bounds")
        if self.minor_units_per_major <= 0 or not self.company or not self.currency:
            raise ValueError("invalid business or currency configuration")
        ZoneInfo(self.timezone)
        for values in (self.segments, self.channels):
            if not values or len(values) != len(set(values)) or any(not v for v in values):
                raise ValueError("segments and channels must be nonempty unique labels")
        if not self.buckets or len({b[0] for b in self.buckets}) != len(self.buckets):
            raise ValueError("DPD bucket labels must be unique")
        expected = 0
        for index, (label, low, high) in enumerate(self.buckets):
            if not label or low != expected or (high is not None and high < low):
                raise ValueError("DPD buckets must be contiguous and nonoverlapping")
            if high is None:
                if index != len(self.buckets) - 1:
                    raise ValueError("only final bucket may be unbounded")
            else:
                expected = high + 1
        if self.buckets[-1][2] is not None:
            raise ValueError("final DPD bucket must be unbounded")

    def bucket(self, dpd: int) -> str:
        """Return the unique configured bucket for nonnegative DPD."""
        if dpd < 0:
            raise ValueError("DPD cannot be negative")
        for label, low, high in self.buckets:
            if low <= dpd and (high is None or dpd <= high):
                return label
        raise ValueError("DPD outside configured buckets")


def load_config(path: Path) -> SimulationConfig:
    """Load YAML; real-data mode is intentionally unsupported."""
    with path.open(encoding="utf-8") as handle:
        raw: Any = yaml.safe_load(handle)
    if not isinstance(raw, dict) or raw.get("simulated") is not True:
        raise ValueError("simulation config must explicitly set simulated: true")
    raw = dict(raw)
    raw.pop("simulated")
    raw["as_of_date"] = date.fromisoformat(str(raw["as_of_date"]))
    raw["segments"] = tuple(raw["segments"])
    raw["channels"] = tuple(raw["channels"])
    raw["buckets"] = tuple(
        (item["label"], item["minimum"], item["maximum"])
        for item in raw.pop("dpd_buckets")
    )
    return SimulationConfig(**raw)


def generate(config: SimulationConfig) -> dict[str, pd.DataFrame]:
    """Generate one loan per borrower and weekly exposure/payment/reminder grains."""
    rng = random.Random(config.seed)
    records: dict[str, list[dict[str, Any]]] = {
        "borrowers": [], "loans": [], "exposures": [], "payments": [], "reminders": []
    }
    this_monday = config.as_of_date - timedelta(days=config.as_of_date.weekday())
    start = this_monday - timedelta(weeks=config.weeks)
    for index in range(config.loan_count):
        borrower_id, loan_id = f"B{index:07d}", f"L{index:07d}"
        principal = rng.randint(config.principal_min_minor, config.principal_max_minor)
        due_date = start - timedelta(days=rng.randint(0, 120))
        arm = rng.choice(("morning", "evening"))
        records["borrowers"].append({
            "borrower_id": borrower_id, "segment": rng.choice(config.segments), "arm": arm
        })
        records["loans"].append({
            "loan_id": loan_id, "borrower_id": borrower_id,
            "principal_minor": principal, "due_date": due_date.isoformat(),
            "origination_date": (due_date - timedelta(days=90)).isoformat(),
        })
        outstanding = principal
        for week in range(config.weeks):
            week_start = start + timedelta(weeks=week)
            exposure_id = f"{loan_id}-W{week:03d}"
            dpd = max(0, (week_start - due_date).days) if outstanding else 0
            recovered = rng.randint(0, outstanding // 5) if outstanding else 0
            # This baseline has no treatment effect; the experiment task adds a prespecified DGP.
            records["exposures"].append({
                "exposure_id": exposure_id, "loan_id": loan_id,
                "week_start": week_start.isoformat(), "opening_minor": outstanding,
                "closing_minor": outstanding - recovered, "dpd": dpd,
                "dpd_bucket": config.bucket(dpd),
            })
            records["payments"].append({
                "payment_id": f"P-{exposure_id}", "exposure_id": exposure_id,
                "loan_id": loan_id, "amount_minor": recovered,
                "payment_date": (week_start + timedelta(days=6)).isoformat(),
                "status": "settled" if recovered else "no_payment",
            })
            records["reminders"].append({
                "reminder_id": f"R-{exposure_id}", "exposure_id": exposure_id,
                "loan_id": loan_id, "channel": rng.choice(config.channels),
                "reminder_date": (week_start + timedelta(days=1)).isoformat(),
                "arm": arm,
            })
            outstanding -= recovered
    frames = {name: pd.DataFrame(rows) for name, rows in records.items()}
    for frame in frames.values():
        frame["simulated"] = True
        frame["company"] = config.company
    return frames


def write_dataset(config: SimulationConfig, config_path: Path) -> dict[str, str]:
    """Write reproducible CSV bytes and their source/config provenance manifest."""
    output = Path(config.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    for name, frame in generate(config).items():
        content = frame.to_csv(index=False, lineterminator="\n").encode("utf-8")
        (output / f"{name}.csv").write_bytes(content)
        hashes[f"{name}.csv"] = hashlib.sha256(content).hexdigest()
    manifest = {
        "simulated": True, "company": config.company, "seed": config.seed,
        "as_of_date": config.as_of_date.isoformat(), "timezone": config.timezone,
        "currency": config.currency, "minor_units_per_major": config.minor_units_per_major,
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "files": hashes,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return hashes


def main() -> None:
    """Generate simulation files from the chosen YAML configuration."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config/simulation.yaml"))
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        hashes = write_dataset(config, args.config)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, f"Simulation failed: {exc}\n")
    print(json.dumps(hashes, sort_keys=True))


if __name__ == "__main__":
    main()
