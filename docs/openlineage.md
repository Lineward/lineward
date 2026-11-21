# Exporting lineage to a catalog (OpenLineage)

`lineward export-lineage --format openlineage` writes your dbt™ project's model and column lineage as
[OpenLineage](https://openlineage.io) events, one JSON object per line (JSON Lines), for your governance catalog to
load. It reads your project's files, as every other command does: no warehouse, no dbt™ run, and nothing is sent
anywhere. The file is yours to load. It needs a key in `LINEWARD_LICENSE_KEY`, and exits 3 without one.

```bash
lineward export-lineage --format openlineage --namespace snowflake://acme-analytics --output lineage.jsonl
```

Name the relations as your production runs build them: the global `--target prod` (and `--profiles <file>` when your
CI keeps its `profiles.yml` elsewhere) goes before or after the command's name, as dbt™'s own flags do.

## What the file holds

- **One event per model, seed and snapshot**, each after the events of the models it reads, the order of their dbt™
  unique ids where that leaves a choice. By default (`--events run`) each is
  a `RunEvent` with `eventType: COMPLETE`, marked design-time by a `designTime` run facet
  (`{"executed": false, "method": "STATIC_ANALYSIS"}`): no statement ran, the lineage is what the code declares. Its
  `runId` depends only on the job and its code, so exporting unchanged code twice gives the same runs. With
  `--events job`, each node is a `JobEvent`, the lineage declared, after a `DatasetEvent` per source table with its
  columns and description.
- **The job** is named by the dbt™ unique id (`model.shop.fct_orders`) in the namespace `--job-namespace` gives,
  `dbt` by default; it carries its type (`MODEL`, `SEED`, `SNAPSHOT`), its compiled SQL (left out with `--no-sql`), its
  description, and with `--repo-url <url of the project in its repository>` the link to its file.
- **Every dataset** is named `DATABASE.SCHEMA.IDENTIFIER` in the namespace `--namespace` gives, your Snowflake account:
  `snowflake://<org>-<account>`, or a legacy account locator. Names are written as Snowflake stores them, unquoted
  parts upper-cased; `--case preserve` writes them as dbt™ configured them, as `dbt-ol` does.
- **The output dataset** carries its columns and types (`schema`), its description (`documentation`), and its column
  lineage twice, in two facets that state the same edges, so each catalog reads the one it knows:
  - `columnLineage`, per column its input fields, each with its transformations: `DIRECT` (`IDENTITY`,
    `TRANSFORMATION`, `AGGREGATION`), and `INDIRECT` `CONDITIONAL` or `WINDOW` when the input decides the value without
    being it. Beside them, the older per-column `transformationDescription` (the column's SQL expression) and
    `transformationType: IDENTITY` for a column copied unchanged. The inputs that decide which rows the model outputs,
    rather than a column's value, are listed once under `dataset`: `INDIRECT` `JOIN`, `FILTER`, `GROUP_BY` and `SORT`.
  - `lineage`, the newer facet: every dataset read, then each row-deciding field with its transformations under
    `inputs`; each column's input fields under `fields`.
- **Sources** appear only as inputs, with their columns and description in run events, and as dataset events in job
  events. Ephemeral models never appear: what reads one reads its inputs.

## What is left out, and said

The export never guesses. What it cannot establish is left out of the file and reported on stderr, one line each:

- a node whose relation name is partly a guess — a `var()` or an `env_var()` with no value, a profile target your
  command did not select, a naming macro that failed. What reads it is still written, without that input.
  `--keep-guessed-names` writes it with its guessed name, every guess still reported, for you to fix by script;
- a column whose lineage is not known for certain, and a node whose rows are not, which keeps its dataset-level
  inputs only;
- the SQL of a node when it is not the SQL dbt™ compiles;
- a type nothing establishes;
- Python models and installed packages' nodes, which are skipped; disabled models and exposures, which are not exported.

In CI, `--strict` exits 1 when anything but a type was left out, after writing the file.

## Loading it

You post each line to your catalog's OpenLineage endpoint, or import the file where the catalog takes one, **in the
file's order**: a catalog that links a column to its input only when it already knows the input's columns (Marquez
does) loses the column lineage of every event it receives before its upstream's. For an HTTP endpoint, one request
per line, for example:

```bash
while IFS= read -r event; do
  curl --fail -sS -X POST -H 'Content-Type: application/json' --data "$event" "$OPENLINEAGE_URL"
done < lineage.jsonl
```

Three transforms with [`jq`](https://jqlang.org) adapt the file to a consumer; each still gives valid events:

```bash
# A START before each COMPLETE, for a consumer that drops a COMPLETE it saw no START for
jq -c '(.eventType = "START"), .' lineage.jsonl > with-start.jsonl
# Model-level lineage only: no column lineage, for a consumer that limits an event's size or its links
jq -c 'del(.outputs[]?.facets.columnLineage, .outputs[]?.facets.lineage)' lineage.jsonl > models-only.jsonl
# UNKNOWN where a column's type is left out, for a consumer that refuses a schema field with no type
jq -c '(.inputs[]?, .outputs[]?) |= (if .facets.schema.fields then .facets.schema.fields |= map(.type //= "UNKNOWN") else . end)' \
  lineage.jsonl > typed.jsonl
```

The third writes a value the export does not know: the catalog shows those columns as of unknown type.

## Known consumer behaviour

Three rows were checked on 2026-10-26 by loading an export into the version they name; the others restate what the
consumer's documentation said on 2026-10-25, **untested**. A consumer's release can change either: check yours before
relying on it.

| Consumer | Where it takes events | What it reads, what it ignores | Transform | Status |
|---|---|---|---|---|
| Marquez | `POST /api/v1/lineage` | Run events: column lineage for the columns of the `schema` facet, with the per-column `transformationDescription`; a column is linked to an input only once Marquez holds the input's columns, so load the file in its order. Job events: the model-level graph alone. Ignores `dataset` and the `lineage` facet | none | **tested**, 0.50.0 |
| DataHub | `POST /openapi/openlineage/api/v1/lineage` | Run events only, each shown as a successful run; refuses every event until its server sets `DATAHUB_OPENLINEAGE_ORCHESTRATOR` (`dbt`, say); each input's `transformations`; drops a dataset whose name holds a double quote or a space, with its edges; keeps the columns' types, not their descriptions or the `documentation` facets | set `DATAHUB_OPENLINEAGE_ORCHESTRATOR` | **tested**, v1.8.0 |
| OpenMetadata | `POST /api/v1/openlineage/lineage` | `COMPLETE` events only; links only tables already in it (a Snowflake ingestion), matched by name with its quotes, so a quoted identifier does not match; refuses a whole event when a `schema` field has no `type`; `inputFields` and the per-column `transformationDescription`; no edge for an event with no input, so seeds are not loaded | UNKNOWN type | **tested**, 2.0.6 |
| Egeria | its OpenLineage integration | Run, job and dataset events; each input's `transformations`, else the per-column fields; the `lineage` facet | none | **untested** |
| Snowflake (external lineage) | its external-lineage REST API | `COMPLETE` events only; `inputFields` on a best-effort basis; says it does not support OpenLineage version 2, which most likely means no job or dataset events | use run events | **untested** |
| Atlan | its OpenLineage connection | Needs a `START` before each `COMPLETE`; reads `DIRECT` inputs only | `START` | **untested** |
| Google Cloud (Data Lineage) | its OpenLineage run-event API | At most 100 links per event; custom events at table level | model-level only, for a larger model | **untested** |
| AWS (Amazon DataZone, SageMaker Unified Studio) | its post-lineage-event API | Run events only; at most 300,000 characters per event | `--no-sql` or model-level only, for a larger event | **untested** |
| Collibra | its OpenLineage integration | Each input's `transformations`, with their subtype and description | none | **untested** |
| IBM (watsonx.data intelligence) | a `.zip` import | Job and dataset events only | `--events job` | **untested** |
| Alation | its OpenLineage API | `COMPLETE` events only, with at least one input and one output, so seeds are not loaded | none | **untested** |

The specification of the command, its options and exit codes, is `lineward export-lineage --help`.
