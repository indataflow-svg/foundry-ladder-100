import time

from ladder.csv_profiler import column_top_values


def test_benchmark_budget() -> None:
    start = time.monotonic()
    for _ in range(1000):
        column_top_values("a,b\n1,x\n", "a", 0)
    assert time.monotonic() - start < 30.0
