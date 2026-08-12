# Synthetic engineering report fixtures

This directory contains expected deterministic Markdown reports generated from the repository's existing public synthetic RunRecord fixtures. The files are regression-test snapshots, not production reports or engineering conclusions.

The source records remain under [`../synthetic_data/`](../synthetic_data/) and [`../synthetic_dataset_v0_1/runs/quality_cases/`](../synthetic_dataset_v0_1/runs/quality_cases/). No real fab, customer, equipment, recipe, process-window, or private-platform data belongs here.

The expected reports are compared byte-for-byte by `tests/test_engineering_report.py`.
