# Healthcare EDI 834 Data Pipeline & Operations Audit

Production-ready data validation and operations framework for **ANSI 5010 EDI 834 (Benefit Enrollment and Maintenance)** transaction sets. Designed to automate healthcare data ingest, identify schema and demographic discrepancies, and maintain compliance standards across payor, TPA, and provider data exchanges.

## Overview
Healthcare data operations require rigorous reconciliation to avoid coverage gaps, claims rejections (EDI 837), and compliance liabilities under HIPAA guidelines. This pipeline:
- Ingests raw ANSI X12 5010 834 inbound files.
- Validates syntax delimiters, loops (2000/2100/2300), and segment integrity.
- Normalizes raw segment data into a relational SQL data model.
- Executes automated operational data quality audits (KPI reporting, eligibility discrepancies, duplicate enrollment detection).

## Architecture & Directory Structure
```text
healthcare-edi-data-pipeline/
│
├── data/
│   └── sample_834.edi          # Synthetic ANSI 5010 834 transaction feed
├── scripts/
│   └── validator.py            # EDI parsing, business rule validation & DB loader
├── sql/
│   └── schema_and_audit.sql    # Relational DDL and reconciliation queries
└── README.md                   # Operational documentation and setup
