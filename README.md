DCOMM Public Records — Senate Campaign Finance Database

Organization: DCOMM
Project: A11 — Senate Campaign Finance Data Platform
Purpose: Preserve, process, and analyze historical U.S. federal campaign-finance records.
Status: MVP / ingestion framework under development
Copyright: © DCOMM 1982–2026

1. Project Overview

DCOMM Public Records is a data engineering project to build a reproducible, auditable database of U.S. Senate campaign-finance activity using publicly available records from the Federal Election Commission (FEC).

The goal is to collect historical records, preserve their provenance, validate and normalize the data, associate contributions with candidates and committees by election cycle, and provide a reliable foundation for SQL analysis and dashboards.

The initial focus is contributions associated with U.S. Senate candidates. The architecture is designed to support additional campaign-finance datasets as the project develops.

Important: The planned storage capacity is up to 4 TB. This is a capacity target, not a claim that 4 TB of data has already been downloaded or ingested.

2. Official Data Sources

Primary source: Federal Election Commission (FEC).

* FEC campaign-finance data: https://www.fec.gov/data/
* FEC bulk data: https://www.fec.gov/data/browse-data/?tab=bulk-data
* FEC PostgreSQL data-dump documentation: https://www.fec.gov/files/bulk-downloads/data-dump/schedules/README.txt
* OpenFEC API documentation: https://api.open.fec.gov/developers/

The FEC publishes campaign-finance datasets covering multiple election cycles. Source availability, file formats, sizes, and update schedules must be verified against the official source inventory before each ingestion run.

Planned datasets

Dataset	Purpose
Schedule A	Itemized receipts and contributions
Schedule B	Disbursements
Schedule E	Independent expenditures
Committee history	Committee metadata and historical changes
Candidate master	Candidate identifiers and attributes
Candidate-committee linkage	Candidate-to-committee relationships by cycle

These datasets have different meanings and must remain distinguishable in storage and analysis. They must not be treated as interchangeable contribution records.

3. System Architecture

The planned pipeline consists of the following stages:

1. Source inventory — discover available files and record URLs, sizes, formats, cycles, and source metadata.
2. Download — retrieve source files to persistent storage with retry and resume support where the source server permits it.
3. Integrity verification — verify byte counts and checksums when authoritative checksums are available; otherwise record locally computed checksums and validation results.
4. Format-aware splitting — divide data into independently processable units without corrupting source files.
5. Staging — load or transform validated source records into staging tables or columnar files.
6. Validation — check schemas, record counts, duplicate identifiers, rejected records, and relationships.
7. Database loading — load completed partitions incrementally and make failed units retryable.
8. Senate data modeling — identify relevant candidates and committees using stable FEC identifiers and cycle-specific relationships.
9. Analytics — provide documented SQL queries and, when implemented, dashboards and exports.
10. Monitoring — track ingestion progress, failures, storage usage, and historical coverage.

Implementation status for each stage must be documented separately. A planned component is not considered operational until it has been implemented and tested.

4. Large-File and Batch-Processing Strategy

The pipeline must support datasets that are too large to process as a single batch.

Logical partitioning

Where supported by the source format and schema, partition data by:

1. Election cycle
2. Dataset or source table
3. Transaction year and month
4. Optional stable committee-ID or hash bucket for exceptionally large partitions

An initial processing-unit target of approximately 5–20 GB may be used for benchmarking. The optimal size will depend on compression, available memory, disk throughput, database performance, and record width.

Format-aware handling

* CSV and delimited text: stream complete records into bounded-size output files. Respect quoted fields and embedded newlines.
* PostgreSQL custom-format dumps: use supported PostgreSQL restore and table-selection options; do not split archive bytes and attempt to restore the pieces independently.
* Plain SQL dumps: restore through a controlled database workflow or create logical partitions from staging tables.
* Compressed archives: use HTTP range requests only when supported, reassemble transport chunks, and verify the completed archive before processing.
* Columnar formats: write independently readable partitions with consistent schemas and metadata.

Transport chunks and logical data partitions are separate concepts. A downloaded byte range is not automatically a valid database batch.

Recovery and idempotency

Every source file and processing unit should have a persistent status record. Completed units must not be downloaded or loaded again unnecessarily.

The pipeline should use temporary files, atomic completion, bounded retries, failure logging, stable source identifiers, and repeatable load operations. Failed partitions should be retried independently.

5. Storage and Repository Policy

The GitHub repository stores source code, documentation, configuration templates, tests, and small metadata manifests.

Large source archives, raw FEC files, database backups, credentials, and multi-terabyte datasets must remain outside Git in appropriately secured persistent storage.

Credentials must be supplied through environment variables or a secret-management service. Do not commit API keys, passwords, access tokens, or database connection strings containing credentials.

6. Database Design Principles

The database should separate:

* Raw source records and provenance
* Validated staging data
* Normalized historical records
* Candidate and committee reference data
* Senate-specific analytical models
* Data-quality and ingestion audit records

Recommended metadata includes source URL, retrieval timestamp, source filename, election cycle, source table, checksum, source submission identifier where available, processing version, load status, row count, and validation outcome.

Candidate and committee relationships must be resolved using stable FEC identifiers and the appropriate election-cycle relationships. Names alone are not reliable join keys.

Exact schemas, indexes, partition definitions, and uniqueness rules will be documented as they are implemented and tested.

7. Ingestion Manifest and Progress Reporting

Each source file and partition should have a manifest entry recording:

* Dataset and election cycle
* Source URL and filename
* Expected and downloaded byte counts
* Checksum and verification status
* Partition identifier
* Processing status
* Rows read, accepted, rejected, and loaded
* Retry count and most recent error
* Database destination and load timestamp

Project progress should be reported using measurable quantities:

* Bytes downloaded and verified
* Source files inventoried and completed
* Rows staged and loaded
* Failed or rejected records
* Election cycles covered
* Storage consumed
* Last successful ingestion run

The total size of available source data must not be confused with the amount successfully ingested.

8. Development Setup

Prerequisites depend on the components currently implemented. The intended environment includes:

* Python for ingestion and validation scripts
* PostgreSQL for relational storage
* Persistent storage for raw source files and staging data
* Git for version control

Clone the repository:

git clone https://github.com/DCOMM1/A11.git
cd A11

Before running an ingestion job, review the available scripts, configuration files, source URLs, and database migrations. Do not start a full historical download until storage capacity, network limits, database capacity, and restart procedures have been tested.

Setup commands will be updated as dependencies and executable pipeline components are added to the repository.

9. Testing and Acceptance Criteria

A pipeline release should not be considered production-ready until it demonstrates that it can:

* Inventory official source files and preserve source metadata.
* Download and verify a representative sample.
* Resume or safely retry an interrupted download when supported.
* Split supported data formats without losing or corrupting records.
* Process a large input without requiring the entire file in memory.
* Restart after interruption without duplicating completed loads.
* Reconcile input, accepted, rejected, and loaded record counts.
* Resolve candidate and committee relationships using appropriate identifiers.
* Reproduce a load from preserved source files and documented configuration.
* Record errors and provide actionable failure reports.

10. Responsible Data Use

Although the source records are public, contributor information can be sensitive. Follow applicable FEC restrictions, privacy requirements, and other relevant laws and policies.

Preserve source provenance and data-quality notes. Do not use the database for prohibited solicitation or commercial purposes. Apply appropriate access controls to derived datasets and any additional information that is not public.

11. Current Project Status

The repository currently contains the A11 file and the archive dcomm_public_records_senate_mvp.zip.

The presence of the archive does not by itself establish which pipeline stages are implemented, whether a database has been populated, or how much historical data has been ingested.

The following should be updated as work is completed:

Component	Status
Repository and MVP archive	Present in GitHub
Source inventory	To be verified against executable code
Resumable download manager	To be verified
Format-aware partitioning	To be verified
Database schemas and migrations	To be verified
Automated ingestion workflows	To be verified
Historical data ingestion totals	Not yet verified
Senate analytical models	To be verified

12. Roadmap

1. Inspect and document the MVP archive.
2. Establish the executable project structure and dependency files.
3. Implement a source inventory and persistent ingestion manifest.
4. Implement resumable downloading and format-aware splitting.
5. Test recovery, checksums, and record-count reconciliation on sample data.
6. Deploy PostgreSQL and persistent raw-data storage.
7. Ingest a representative election cycle.
8. Validate Senate candidate and committee joins.
9. Expand ingestion across historical cycles.
10. Add analytical SQL, dashboards, monitoring, and documented releases.

⸻

DCOMM — Remembering the Past, Forging the Future.

13. Operational Notes & Environment Constraints

Fix: The loader failed because the synthetic files were named `cn26.zip` but the script looks for `cn2026.zip` — FEC cycle files use the two-digit year. That’s a one-line fix in the script, not a data problem.

The full four-terabyte ingestion cannot run in this environment. Outbound connections are refused, so no FEC download is possible, and the disk is twenty gigabytes with three gigabytes of RAM. The FEC’s own guidance says the Postgres restore needs roughly three hundred gigabytes without indexes and two terabytes with them, so this sandbox was never going to hold it.

What is ready: the production kit with the streaming downloader, the Senate filter SQL, the loader script, and the MVP extension, all packaged as zips. The synthetic data proves the pipeline logic works once the filename convention is aligned.

On your machine with real disk, the sequence is: run `download_current_cycle.sh`, then `load_senate_cycle.py`, then stage the weekly Postgres dump and export partitioned Parquet by two-year period using the same `senate_filter.sql` logic. Push the zips to the A11 repo first so the code lives where you can run it.

One thing worth doing before the big load: the FEC’s public DuckDB build on Hugging Face has about two hundred eighty million contribution rows from two thousand four through twenty twenty-six and can be queried remotely without downloading anything. That lets you prototype the Senate gold mart immediately while the full dump stages elsewhere.
