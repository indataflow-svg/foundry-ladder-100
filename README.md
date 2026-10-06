# foundry-ladder-100

Single-repo 100-PR ladder target: fourteen independent utility scopes,
each one module plus its tests. One scope per PR keeps every merge
collision-free by construction.

## Scope map

| Scope | Module | Responsibility |
|---|---|---|
| csv_profiler | `ladder.csv_profiler` | Column stats for CSV text |
| jsonl_metrics | `ladder.jsonl_metrics` | Group-by aggregation over JSONL |
| text_redactor | `ladder.text_redactor` | Pattern redaction + audit report |
| time_series | `ladder.time_series` | Bucket resampling, rolling means |
| money | `ladder.money` | Fixed-point money arithmetic |
| password_policy | `ladder.password_policy` | Validation + strength score |
| retry_policy | `ladder.retry_policy` | Backoff and jitter schedules |
| rate_limiter | `ladder.rate_limiter` | Token-bucket limiter, pure clock |
| csv_differ | `ladder.csv_differ` | Row-level CSV diff on a key |
| config_loader | `ladder.config_loader` | Layered config + schema validation |
| markdown_toc | `ladder.markdown_toc` | TOC builder, fences excluded |
| log_sampler | `ladder.log_sampler` | Deterministic reservoir sampling |
| unit_converter | `ladder.unit_converter` | Length / mass / temperature |
| chunker | `ladder.chunker` | Overlapping text chunking |

## Contributing (ladder rules)

- One PR touches exactly one scope (plus its tests).
- Every PR keeps `pytest`, `ruff check`, `ruff format --check`, and
  `mypy src` green — CI enforces all four.
- No filler: every change must do real work a reviewer would accept.
