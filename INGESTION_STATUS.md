# DCOMM A11 — Ingestion Status

Status: NOT STARTED

Target for first controlled batch: maximum 2,000,000,000 bytes (decimal 2 GB).

This status file does not indicate that any FEC records have been downloaded or loaded. Before ingestion, an executable workflow must be configured to fetch official FEC source files, enforce the byte cap, validate checksums/record counts, and persist data outside Git history. The ChatGPT execution environment cannot download the multi-gigabyte FEC dataset directly.

Planned first source: official FEC itemized individual contributions (Schedule A) for the 2026 cycle, subject to verifying the published archive size and format.
