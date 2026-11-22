"""Time the baseline. Run: python scripts/benchmark.py [path-to-csv]"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from popularity import load_interactions, top_products

path = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "data" / "interactions.csv"
t = time.perf_counter(); df = load_interactions(path); load_s = time.perf_counter() - t
runs = 200
t = time.perf_counter()
for _ in range(runs):
    top_products(df, 5)
avg_ms = (time.perf_counter() - t) / runs * 1000
print(f"rows={len(df)}  load={load_s*1000:.1f} ms  top_products avg={avg_ms:.2f} ms over {runs} runs")
