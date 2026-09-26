---
id: P1-01
skill: P1
stage: 1
title: "The stack end to end: from a source system to a dashboard"
minutes: 75
prerequisites: []
audience: all
skippable: true
sources:
  - repo: orchestration
    path: README.md
    commit: "ea713797fe70d68779f9116577dda81dddcc4e6f"
  - repo: warehouse
    path: README.md
    commit: "9efbb8b979e3be90ded565726fba8da7597fd115"
  - repo: orchestration
    path: docs/risk-register.md
    commit: "ea713797fe70d68779f9116577dda81dddcc4e6f"
---

# The stack end to end: from a source system to a dashboard

## Why this matters here

On one night in August 2026, the job that pushes data to the HubSpot CRM **fired while
the mart layer was still being rebuilt**. It pushed a half-built set of tables: some from
that night's build, at least one nearly 18 hours old. Nothing crashed. An operator found it
by reading a list of sensor ticks (risk **ORCH-73** in `orchestration`
`docs/risk-register.md`).

This kind of problem is only visible to someone who knows the order things happen in: where
data lands, what transforms it, when the marts are finished, and what reads them. This unit
builds that picture.

## The concept

A modern data stack moves data in three steps, often called **ELT**:

1. **Extract and load.** Copy data from source systems (the SIS, the LMS, surveys) into the
   warehouse as-is.
2. **Transform.** Inside the warehouse, clean, join and reshape the raw tables into tables
   people can use.
3. **Serve.** Dashboards, spreadsheets and other tools read the finished tables.

An **orchestrator** decides when each step runs and in what order.

## How it looks in our stack

All of this comes from the two READMEs.

- **Sources:** Veracross (the SIS), MARIO, Toddle, ManageBac, Google Sheets, NWEA MAP, College
  Board, IB and parent surveys (warehouse `README.md`, opening paragraph and "How it fits into
  the stack").
- **Extract and load:** **dlt** pipelines running inside the Dagster container load straight to
  BigQuery, into datasets named `data_import_dlt_*`. Airbyte did this until June 2026
  (orchestration `README.md`, "What's in this repo"). Veracross Data Packages and CSVs arrive
  through Google Cloud Storage.
- **Transform:** **dbt** rebuilds the warehouse in layers, **staging → intermediate → mart**
  (warehouse `README.md`, "How it fits into the stack"). The dbt code lives in the `warehouse`
  repo, and the production run **clones it fresh at run time** rather than keeping a copy
  (orchestration `README.md`, "What's in this repo").
- **Where the finished tables live:** dev builds target the `ais-data-warehouse` project, and
  production marts are built in a separate project, `ais-data-mart` (warehouse `README.md`).
- **Serve:** Looker Studio dashboards, connected Sheets and AppSheet apps read the marts
  (warehouse `README.md` diagram).
- **Orchestrate:** **Dagster** on one Google Cloud VM. Most pipelines start when a file
  **arrives** in Cloud Storage, not at a fixed time. The main AIS Warehouse pipeline starts when
  Veracross files land under `data_import_vx/*`. Google Workspace is the exception and runs on
  a 2 AM schedule (orchestration `README.md`, "The data flow").

## Lab

See [lab.md](lab.md). You'll put the stack in order and prove three facts from the files.

## Check questions

Three quick questions after the lab (`content/questions/P1.yaml`, pool `unit`).

## Ask the tutor

- "Why does the stack load raw data first and transform it afterwards?"
- "What is the difference between the `ais-data-warehouse` and `ais-data-mart` projects?"
- "Why would a pipeline start when a file arrives instead of at a fixed time?"
