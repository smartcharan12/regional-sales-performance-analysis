"""
Tests that prove the cleaning is correct, not just "plausible".

Because the dataset is generated, we have something real projects rarely
have: the error-free version of the data (before problems were injected).
So we can check that every value the cleaning REPAIRED equals the truth,
and that every row it REMOVED was genuinely broken.

Run from the project root:
    python tests/test_pipeline.py          (no extra libraries needed)
    python -m pytest tests/                (if you have pytest installed)
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import generate_data  # noqa: E402
from build_star_schema import build_star_schema  # noqa: E402
from data_cleaning import clean_sales_data, count_repaired_values  # noqa: E402
from eda import kpi_summary, summarize_by  # noqa: E402
from feature_engineering import engineer_features  # noqa: E402
from utils import POWERBI_EXPORT, RAW_FILE  # noqa: E402

KEY = ["Order ID", "Product ID"]

# Build everything once and share it between tests
_truth = generate_data.build_clean_orders(np.random.default_rng(generate_data.SEED))
_raw = pd.read_csv(RAW_FILE)
_clean, _log = clean_sales_data(_raw)
_clean = engineer_features(_clean)


def test_raw_file_matches_generator():
    """The committed raw file is byte-for-byte what the seeded generator produces."""
    rng = np.random.default_rng(generate_data.SEED)
    regenerated = generate_data.inject_quality_issues(generate_data.build_clean_orders(rng), rng)
    assert regenerated.to_csv(index=False, lineterminator="\n") == RAW_FILE.read_text(encoding="utf-8")


def test_no_rows_invented():
    """Every clean row exists in the true data (cleaning never creates sales)."""
    merged = _clean[KEY].merge(_truth[KEY], on=KEY, how="left", indicator=True)
    assert (merged["_merge"] == "both").all()
    assert not _clean.duplicated(subset=KEY).any()


def test_repaired_values_equal_truth():
    """Region, Category, names, Sales, Discount and Profit match the truth."""
    m = _clean.merge(_truth, on=KEY, suffixes=("", "_true"))
    assert len(m) == len(_clean)
    for col in ["Region", "Category", "Customer Name", "Product Name", "City"]:
        assert (m[col] == m[f"{col}_true"]).all(), f"{col} differs from truth"
    for col in ["Sales", "Discount", "Profit"]:
        assert np.allclose(m[col], m[f"{col}_true"]), f"{col} differs from truth"


def test_removed_rows_are_few_and_logged():
    """Only rows that could not be repaired were removed, and the log adds up."""
    lost = len(_truth) - len(_clean)
    logged = _log.loc[_log["step"] != "Remove exact duplicates", "rows_removed"].sum()
    assert lost == logged, "every removed real row must appear in the log"
    assert lost / len(_truth) < 0.005, "more than 0.5% of real rows removed"


def test_totals_close_to_truth():
    """Headline totals are within 1% of the error-free data."""
    for col in ["Sales", "Profit"]:
        assert abs(_clean[col].sum() / _truth[col].sum() - 1) < 0.01


def test_margin_is_weighted():
    """Group margins in eda.summarize_by must be SUM(Profit)/SUM(Sales) per group,
    not the average of row-level margins (which gives a different, wrong answer)."""
    region = summarize_by(_clean, "Region")
    for name, g in _clean.groupby("Region"):
        expected = g["Profit"].sum() / g["Sales"].sum() * 100
        assert np.isclose(region.loc[name, "Profit Margin %"], expected, atol=0.01)
    assert not np.isclose(region.loc["Central", "Profit Margin %"],
                          _clean.loc[_clean["Region"] == "Central", "Profit Margin %"].mean(), atol=0.5)


def test_repaired_value_count():
    """Each repaired cell counted once (the figure quoted in the docs)."""
    assert count_repaired_values(_raw, _clean).sum() == 275


def test_documented_numbers():
    """The headline numbers quoted in README, reports and DAX validation files.
    If the data or logic changes, this test fails and the docs must be updated."""
    k = kpi_summary(_clean)
    assert len(_raw) == 11_567 and len(_clean) == 11_461
    assert round(k["Total Sales"], 2) == 4_391_176.00
    assert round(k["Total Profit"], 2) == 452_068.04
    assert round(k["Profit Margin %"], 2) == 10.29
    assert k["Total Orders"] == 5_190 and k["Total Quantity"] == 56_703
    assert round(k["YoY Sales Growth % (2024)"], 2) == 6.69
    assert round(k["YoY Profit Growth % (2024)"], 2) == -6.63
    region = summarize_by(_clean, "Region")
    assert round(region.loc["Central", "Profit Margin %"], 2) == 3.28
    assert round(region.loc["Central", "Effective Discount %"], 2) == 21.51
    deep = _clean[_clean["Discount"] >= 0.3]
    assert round(deep["Profit"].sum(), 2) == -249_356.36
    assert round((deep["Gross Sales"] * (deep["Discount"] - 0.2)).sum(), 2) == 264_266.66


def test_csv_outputs_use_lf_line_endings():
    """CSV files must use \n so MySQL LOAD DATA works the same on Windows and Linux."""
    for path in [RAW_FILE, *POWERBI_EXPORT.glob("*.csv")]:
        assert b"\r\n" not in path.read_bytes(), f"{path.name} has Windows line endings"


def test_star_schema_keeps_every_row():
    tables = build_star_schema(_clean)
    fact = tables["FactSales"]
    assert len(fact) == len(_clean)
    assert np.isclose(fact["Sales"].sum(), _clean["Sales"].sum())
    assert tables["DimDate"]["Date"].is_monotonic_increasing
    assert tables["DimDate"]["Date"].diff().dropna().dt.days.eq(1).all(), "date table has gaps"


if __name__ == "__main__":
    tests = [obj for name, obj in dict(globals()).items() if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}")
    print(f"\n{len(tests)} tests passed")
