"""Load deterministic simulated CSV sources into DuckDB with idempotent replace semantics."""

import argparse
from pathlib import Path

import duckdb


def load_into_duckdb(*, db_path: Path, source_dir: Path) -> dict[str, int]:
    """Create or replace raw tables from generated CSV files and return row counts."""
    required = {
        "borrowers": "borrowers.csv",
        "loans": "loans.csv",
        "exposures": "exposures.csv",
        "payments": "payments.csv",
        "reminders": "reminders.csv",
    }
    missing = [name for name, file_name in required.items() if not (source_dir / file_name).exists()]
    if missing:
        raise FileNotFoundError(f"missing generated CSV files: {', '.join(sorted(missing))}")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    with duckdb.connect(str(db_path)) as conn:
        conn.execute("BEGIN TRANSACTION")
        try:
            conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
            for table, file_name in required.items():
                csv_path = source_dir / file_name
                conn.execute(
                    f"CREATE OR REPLACE TABLE raw.{table} AS SELECT * FROM read_csv_auto(?, header=true)",
                    [str(csv_path)],
                )
                counts[table] = conn.execute(f"SELECT COUNT(*) FROM raw.{table}").fetchone()[0]
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    return counts


def main() -> None:
    """CLI to load generated simulated files into DuckDB."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path("data/warehouse/xyz_finance.duckdb"))
    parser.add_argument("--source", type=Path, default=Path("data/generated"))
    args = parser.parse_args()

    counts = load_into_duckdb(db_path=args.db, source_dir=args.source)
    print(counts)


if __name__ == "__main__":
    main()
