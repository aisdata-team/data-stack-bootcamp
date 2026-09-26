# Lab — Put the stack in order

## Goal

Put the stack's components in the order data flows through them, and prove three facts
about it from the repos.

## Environment

Read-only access to `aisdata-team/orchestration` and `aisdata-team/warehouse` on GitHub. No
cloud access is needed.

## Steps

1. Put these eight components in the order a Veracross record passes through on its way to a
   dashboard:
   - an `ais-data-mart` table
   - Veracross
   - a dbt **staging** model
   - a Looker Studio dashboard
   - a `data_import_dlt_*` table in BigQuery
   - a dbt **intermediate** model
   - a dlt pipeline running in the Dagster container
   - a dbt **mart** model
2. Answer each question below, and cite the **file and section** that proves your answer:
   - **(a)** Where does the dbt code live, and how does the nightly production run get it?
   - **(b)** What event starts the AIS Warehouse pipeline?
   - **(c)** Which one pipeline runs on a fixed schedule instead, and at what time?

## You're done when

The eight components are in the right order, and each answer names a file and a section
heading where a reader can find it stated.

## Evidence

Your ordered list and your three answers with their citations.

## Common mistakes

- **Putting the mart project before the mart model.** The model is the dbt code; the table in
  `ais-data-mart` is what it builds.
- **Citing a file without a section.** "The README" isn't enough, since both repos have one and
  they are long. Name the heading.
- **Answering from memory or a chat answer without opening the file.** The point of the lab is
  that the file says so.

## Reset

Nothing to reset. The lab is read-only.

## Stretch

Open `docs/pipelines/ais-warehouse.md` in orchestration and find one step that runs **between**
the dlt landing and the dbt build. Why might it sit there?
