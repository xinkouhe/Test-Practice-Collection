#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Helpers for reading CSV test data from the project's data directory."""

from __future__ import annotations

import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def _normalize_cell(value: str | None) -> str | None:
    """Normalize empty-like CSV values for test usage."""
    if value is None:
        return None

    cleaned = value.strip()
    if cleaned == "":
        return None
    if cleaned.lower() in {"none", "null"}:
        return None
    return cleaned


def load_csv_rows(filename: str, data_dir: Path = DATA_DIR) -> list[dict[str, str | None]]:
    """Load a single CSV file and return rows as dictionaries."""
    csv_path = data_dir / filename
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(mode="r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file has no header row: {csv_path}")

        return [
            {key: _normalize_cell(value) for key, value in row.items()}
            for row in reader
        ]


def find_csv_files(pattern: str = "test_*.csv", data_dir: Path = DATA_DIR) -> list[Path]:
    """Return matching CSV files from the data directory."""
    return sorted(path for path in data_dir.glob(pattern) if path.is_file())


def auto_load_csv(pattern: str = "test_*.csv") -> list[tuple[str, list[dict[str, str | None]]]]:
    """Compatibility wrapper for loading all matching CSV files."""
    return [(path.name, load_csv_rows(path.name)) for path in find_csv_files(pattern)]
