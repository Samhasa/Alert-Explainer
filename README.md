# Alert Explainer API

The capstone's FastAPI intelligence layer stores monitoring alerts in SQLite and
returns rule-based explanations built from each alert's own fields. It compares
the metric value with its threshold and recommends a next step based on severity.
It does not call an external AI or LLM service.

## Project Structure

```text
.
|-- main.py                 # FastAPI app, table creation, and root endpoint
|-- database.py             # SQLite engine and database session dependency
|-- models.py               # SQLAlchemy Alert model
|-- schemas.py              # Pydantic request and response schemas
|-- requirements.txt        # Runtime dependencies
|-- routers/
|   `-- alerts.py           # Alert and explanation endpoints
|-- services/
|   `-- explainer.py        # Fixed explanation rules
|-- test_alerts.py          # Eight API tests with an in-memory database
|-- docs/
|   `-- adr/
|       |-- 0001-rule-based-explanations.md
|       `-- 0002-human-approval-for-alert-summaries.md
`-- README.md
```

The app creates `alerts.db` in the current working directory and creates missing
tables at import time. Run commands from the project root.

## Alert Fields

| Field | Type | Input and behavior |
| --- | --- | --- |
| `id` | integer | Generated database primary key; returned in responses. |
| `title` | string | Required on creation. |
| `severity` | string | Required; Pydantic restricts it to `critical`, `warning`, or `info`. The database model stores a string. |
| `source` | string | Required on creation. |
| `metric_name` | string | Required on creation. |
| `metric_value` | float | Required on creation. |
| `threshold` | float | Required on creation; zero is supported. |
| `created_at` | datetime | Generated using the current UTC time; returned in responses. SQLite may return it without timezone information. |

Explanation text says the metric `exceeded`, `fell below`, or `reached` its
threshold. Recommended next steps are:

| Severity | Recommended next step |
| --- | --- |
| `critical` | Investigate immediately and take corrective action. |
| `warning` | Review the affected system and monitor the metric closely. |
| `info` | Review the metric and confirm whether any action is needed. |

The acknowledgement text is `Not yet acknowledged` when there is no truthy
`resolved_by` attribute; otherwise that value is uppercased. The current Alert
model and API schemas have no `resolved_by` field or acknowledgement endpoint,
so alerts created through this API use the default acknowledgement text.

## Endpoints

| Method | Path | Successful response | Other expected status codes |
| --- | --- | --- | --- |
| GET | `/` | 200: `{"status":"AI Intelligence Layer is running"}` | None defined. |
| POST | `/alerts/` | 201: created Alert, including `id` and `created_at`. | 422: invalid or missing request fields. |
| GET | `/alerts/` | 200: array of Alerts ordered by ID; empty array if none exist. | None defined. |
| GET | `/alerts/{alert_id}` | 200: matching Alert. | 404: unknown ID; 422: non-integer ID. |
| POST | `/alerts/{alert_id}/explain` | 200: `alert_id`, rule-based `explanation`, and UTC `generated_at` timestamp. No request body. | 404: unknown ID; 422: non-integer ID. |

Both alert-ID endpoints return `{"detail":"Alert not found"}` for an unknown
integer ID. Explanation text is deterministic for the same alert fields;
`generated_at` is produced anew for each explanation request.

FastAPI also provides GET `/docs` (200, Swagger UI), GET `/docs/oauth2-redirect`
(200, Swagger OAuth redirect helper), GET `/redoc` (200, ReDoc), and GET
`/openapi.json` (200, OpenAPI schema).

## Install and Run: Windows PowerShell

Prerequisites: Python 3.10 or newer with `venv` and `pip`. Open PowerShell in the
project root. The test tools are installed separately because `requirements.txt`
lists runtime dependencies only. Initial dependency installation requires access
to a package index or a local package cache; explanation generation itself works
offline.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pytest httpx
uvicorn main:app --reload
```

The server runs at http://127.0.0.1:8000. Open the Swagger UI at
http://127.0.0.1:8000/docs and expand `POST /alerts/{alert_id}/explain` to see its
rule-based description and 404 case. Stop the server with Ctrl+C.

## Install and Run: Linux or macOS

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install pytest httpx
uvicorn main:app --reload
```

The same URLs and Ctrl+C shutdown apply.

## Run Tests

With the virtual environment activated and the server stopped:

```text
python -m pytest test_alerts.py -v
```

Expected result: **8 passed**. The tests use an isolated in-memory SQLite database
and do not need a running server or external LLM service.

## Architecture Decisions

- [ADR 0001: Rule-Based Explanations](docs/adr/0001-rule-based-explanations.md)
- [ADR 0002: Human Approval for Alert Summaries](docs/adr/0002-human-approval-for-alert-summaries.md)

ADR 0002 records the capstone's n8n workflow decision. The n8n workflow, summary
generation, approval gate, and on-call delivery are not implemented in this
repository; this API implements alert storage and individual rule-based
explanations.