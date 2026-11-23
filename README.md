# PureDrop Dairy – Popularity Baseline (Task 2)

The simplest possible recommender: it suggests the same top products to everyone,
ranked by how often they were ordered. Every smarter model built later has to beat
this baseline, so it is kept honest and plain.

## What "popularity" means here
- **Data:** the Task 1 file `data/interactions.csv`
  (`customer_id, product_id, date, slot, quantity, status, amount_pkr`).
- **What is counted:** the number of rows per `product_id`. One row = one product on one
  customer's delivery on one date (the same unit as the Task 1 metrics).
- **Only `status == "delivered"` rows count.** `skipped` and `paused` rows have `quantity = 0`
  and no amount – no order happened, so they must not boost a product.
- **Why not `quantity`?** One customer taking 6 litres would outweigh six customers taking 1 litre.
  Popularity should reflect how many orders chose the product.
- **Ties:** the lower `product_id` ranks first, so results are always the same.
- **Zero delivered rows:** a product with no delivered order lines drops out of the ranking
  (it is not listed with a count of 0). If fewer than `k` products qualify, fewer than `k` are returned.

## Run it
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/popularity.py --data data/interactions.csv --k 5
```

Output on the full Task 1 data (614 rows):
```
 rank  product_id  orders
    1           1     233
    2           2     126
    3           3      82
    4           8      48
    5           7      42
```

## Check it
```bash
python -m pytest -q
```
Expected result: `11 passed`.

- **Main path:** top products come back in the right order, and skipped/paused rows are not counted.
- **Failure paths:** empty input, missing column, no delivered rows, non-numeric `product_id`
  (e.g. `milk`), malformed or empty CSV, bad `k`, missing file
  → a clear message, no crash (the command prints `Error: ...`).
- **Edge case:** a product with zero delivered rows is left out of the ranking.

## Performance
`python scripts/benchmark.py [path-to-csv]` prints load time and average ranking time.

| Data | Rows | Load | Ranking (avg of 200 runs) |
|---|---|---|---|
| Full Task 1 file | 614 | 2.8 ms | 3.2 ms |

Ranking the whole file takes about 3 ms, so speed is not a concern at this size.

## Known limitation
Product 1 accounts for 233 of the 587 delivered orders (about 39.7%), so this baseline
recommends the same top items to every customer. That makes it a useful floor for
later models to beat, but not a usable recommender on its own.
Possible refinements (not built yet): a recent-time window, or counting unique customers.