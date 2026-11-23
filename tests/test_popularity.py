import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from popularity import main, top_products


def sample():
    rows = [  # customer_id, product_id, status
        (1, 1, "delivered"), (2, 1, "delivered"), (3, 1, "delivered"),
        (1, 2, "delivered"), (2, 2, "delivered"),
        (3, 3, "delivered"),
        (4, 3, "skipped"), (5, 3, "paused"), (6, 3, "skipped"), (7, 3, "paused"),  # must NOT count
    ]
    return pd.DataFrame(rows, columns=["customer_id", "product_id", "status"])


# --- main path -------------------------------------------------------------
def test_top_products_in_right_order_and_skipped_not_counted():
    result = top_products(sample(), k=3)
    assert list(result["product_id"]) == [1, 2, 3]
    assert list(result["orders"]) == [3, 2, 1]  # product 3 would be 5 if skipped/paused were counted
    assert list(result["rank"]) == [1, 2, 3]


def test_k_limits_the_list():
    assert len(top_products(sample(), k=2)) == 2


# --- failure paths ---------------------------------------------------------
def test_empty_input_gives_clear_message():
    with pytest.raises(ValueError, match="empty"):
        top_products(pd.DataFrame())


def test_missing_column_gives_clear_message():
    with pytest.raises(ValueError, match="missing required column"):
        top_products(pd.DataFrame({"product_id": [1, 2]}))


def test_no_delivered_rows():
    df = pd.DataFrame({"product_id": [1], "status": ["skipped"]})
    with pytest.raises(ValueError, match="No delivered"):
        top_products(df)


def test_bad_k():
    with pytest.raises(ValueError, match="positive"):
        top_products(sample(), k=0)


def test_cli_does_not_crash_on_missing_or_empty_file(tmp_path, capsys):
    assert main(["--data", str(tmp_path / "nope.csv")]) == 1
    assert "File not found" in capsys.readouterr().err
    empty = tmp_path / "empty.csv"; empty.write_text("")
    assert main(["--data", str(empty)]) == 1
    assert "empty" in capsys.readouterr().err

def test_product_with_zero_delivered_rows_is_left_out():
    df = pd.DataFrame({"product_id": [1, 1, 2, 3],
                       "status": ["delivered", "delivered", "delivered", "skipped"]})
    result = top_products(df, k=5)
    assert list(result["product_id"]) == [1, 2]

def test_tie_lower_product_id_ranks_first():
    df = pd.DataFrame({"product_id": [5, 5, 2, 2, 9], "status": ["delivered"] * 5})
    result = top_products(df, k=3)
    assert list(result["product_id"]) == [2, 5, 9]
    assert list(result["orders"]) == [2, 2, 1]


def test_cli_malformed_csv_gives_clear_message(tmp_path, capsys):
    bad = tmp_path / "bad.csv"
    bad.write_text('product_id,status\n1,"delivered\n')
    assert main(["--data", str(bad)]) == 1
    assert "not a valid CSV" in capsys.readouterr().err


def test_cli_text_product_id_gives_clear_message(tmp_path, capsys):
    f = tmp_path / "text.csv"
    f.write_text("product_id,status\nmilk,delivered\n1,delivered\n")
    assert main(["--data", str(f)]) == 1
    assert "product_id must contain only numbers" in capsys.readouterr().err
