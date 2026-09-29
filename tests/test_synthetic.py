"""Invariant tests for the deterministic simulated source data."""

import json
from dataclasses import replace
from datetime import date
from pathlib import Path

import duckdb
import pandas as pd
import pytest

from copilot.storage import load_into_duckdb
from copilot.synthetic import generate, load_config, write_dataset


@pytest.fixture
def config():
    """Use a small version of the checked-in configuration."""
    return replace(load_config(Path("config/simulation.yaml")), loan_count=12, weeks=3)


def test_fixed_seed_is_reproducible(config):
    first, second = generate(config), generate(config)
    for name in first:
        pd.testing.assert_frame_equal(first[name], second[name])
    assert not first["loans"].equals(generate(replace(config, seed=123))["loans"])


def test_grains_and_foreign_keys(config):
    tables = generate(config)
    for name, key in {
        "borrowers": "borrower_id",
        "loans": "loan_id",
        "exposures": "exposure_id",
        "payments": "payment_id",
        "reminders": "reminder_id",
        "contact_events": "contact_id",
        "ptp_events": "ptp_id",
        "complaints": "complaint_id",
    }.items():
        assert tables[name][key].is_unique
        assert not tables[name].isna().any().any()
        assert tables[name]["simulated"].all()
        assert tables[name]["company"].eq("XYZ Finance").all()
    assert len(tables["loans"]) == config.loan_count
    assert len(tables["exposures"]) == config.loan_count * config.weeks
    assert set(tables["loans"].borrower_id) <= set(tables["borrowers"].borrower_id)
    for name in ("exposures", "payments", "reminders", "contact_events", "ptp_events", "complaints"):
        assert set(tables[name].loan_id) <= set(tables["loans"].loan_id)
        assert set(tables[name].exposure_id) <= set(tables["exposures"].exposure_id)


def test_money_reconciles_without_negative_balance(config):
    tables = generate(config)
    exposures = tables["exposures"]
    joined = exposures.merge(tables["payments"], on="exposure_id", validate="one_to_one")
    assert (joined.opening_minor - joined.amount_minor).equals(joined.closing_minor)
    assert (joined.amount_minor >= 0).all()
    assert (joined.closing_minor >= 0).all()
    previous_close = exposures.groupby("loan_id").closing_minor.shift()
    assert exposures.loc[previous_close.notna(), "opening_minor"].eq(
        previous_close.dropna()
    ).all()
    totals = tables["payments"].groupby("loan_id").amount_minor.sum()
    principal = tables["loans"].set_index("loan_id").principal_minor
    assert totals.le(principal).all()
    assert tables["payments"].payment_date.map(date.fromisoformat).lt(config.as_of_date).all()


def test_bucket_boundaries(config):
    for dpd, label in ((0, "current"), (1, "1-29"), (29, "1-29"), (30, "30-60"),
                       (60, "30-60"), (61, "61-90"), (90, "61-90"), (91, "91+")):
        assert config.bucket(dpd) == label
    with pytest.raises(ValueError, match="negative"):
        config.bucket(-1)
    with pytest.raises(ValueError, match="contiguous"):
        replace(config, buckets=(("a", 0, 30), ("b", 30, None)))


def test_randomization_is_per_borrower(config):
    reminders = generate(config)["reminders"]
    assert reminders.groupby("loan_id").arm.nunique().eq(1).all()


def test_contact_ptp_and_complaints_consistency(config):
    tables = generate(config)
    contacts = tables["contact_events"]
    ptp = tables["ptp_events"]
    complaints = tables["complaints"]

    assert contacts["contacted"].isin([True, False]).all()
    assert ptp["promise_made"].isin([True, False]).all()
    assert ptp["promise_kept"].isin([True, False]).all()
    assert complaints["complaint_filed"].isin([True, False]).all()

    merged = contacts.merge(ptp, on=["loan_id", "exposure_id"], validate="one_to_one")
    assert merged.loc[~merged["contacted"], "promise_made"].eq(False).all()
    assert merged.loc[~merged["promise_made"], "promise_kept"].eq(False).all()

    complaint_dates = complaints.loc[complaints["complaint_filed"], "complaint_date"]
    assert complaint_dates.notna().all()
    no_complaint_dates = complaints.loc[~complaints["complaint_filed"], "complaint_date"]
    assert no_complaint_dates.isna().all()


def test_written_hashes_and_manifest_are_reproducible(config, tmp_path):
    config = replace(config, output_dir=str(tmp_path))
    source = Path("config/simulation.yaml")
    first = write_dataset(config, source)
    manifest_first = (tmp_path / "manifest.json").read_bytes()
    assert first == write_dataset(config, source)
    assert manifest_first == (tmp_path / "manifest.json").read_bytes()
    manifest = json.loads(manifest_first)
    assert manifest["simulated"] is True
    assert manifest["files"] == first
    assert all(len(value) == 64 for value in first.values())


def test_invalid_configuration(config, tmp_path):
    with pytest.raises(ValueError):
        replace(config, loan_count=0)
    with pytest.raises(ValueError):
        replace(config, channels=())
    with pytest.raises(ValueError):
        replace(config, principal_min_minor=-1)
    source = tmp_path / "config.yaml"
    source.write_text("simulated: false\n", encoding="utf-8")
    with pytest.raises(ValueError, match="simulated"):
        load_config(source)


def test_duckdb_load_is_idempotent(config, tmp_path):
    output_dir = tmp_path / "generated"
    config = replace(config, output_dir=str(output_dir))
    write_dataset(config, Path("config/simulation.yaml"))
    db_path = tmp_path / "warehouse.duckdb"

    first = load_into_duckdb(db_path=db_path, source_dir=output_dir)
    second = load_into_duckdb(db_path=db_path, source_dir=output_dir)
    assert first == second

    with duckdb.connect(str(db_path), read_only=True) as conn:
        counts = {
            table: conn.execute(f"SELECT COUNT(*) FROM raw.{table}").fetchone()[0]
            for table in (
                "borrowers",
                "loans",
                "exposures",
                "payments",
                "reminders",
                "contact_events",
                "ptp_events",
                "complaints",
            )
        }
        assert counts == first
        fk_mismatch = conn.execute(
            """
            SELECT COUNT(*)
            FROM raw.exposures e
            LEFT JOIN raw.loans l ON e.loan_id = l.loan_id
            WHERE l.loan_id IS NULL
            """
        ).fetchone()[0]
        assert fk_mismatch == 0
        money_check = conn.execute(
            """
            SELECT COUNT(*)
            FROM raw.exposures e
            JOIN raw.payments p ON e.exposure_id = p.exposure_id
            WHERE e.opening_minor - p.amount_minor <> e.closing_minor
            """
        ).fetchone()[0]
        assert money_check == 0
        with pytest.raises(duckdb.BinderException):
            conn.execute("DROP TABLE raw.loans")


def test_duckdb_loader_rejects_missing_sources(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_into_duckdb(db_path=tmp_path / "warehouse.duckdb", source_dir=tmp_path / "missing")
