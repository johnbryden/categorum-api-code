# Categorum API 

This repository provides a minimal client for exercising the Categorum Jobs API.

## Contents

- `client_wrapper.py`: lightweight wrapper around the Jobs API using `requests`.
- `test_job_submission.ipynb`: notebook that submits and monitors a sample job.

## Setup

Install dependencies:

```
pip install -r requirements.txt
```

Ensure a `.env` file is available with:

- `API_KEY`
- `JOBS_API_BASE_URL`

You can get the API KEY from your categorum account.

## Usage

1. Launch Jupyter Notebook:

   ```
   jupyter notebook
   ```

2. Open `test_job_submission.ipynb` and enter your own SHEET_ID. Run the cells in order to:
   - Load environment variables.
   - Instantiate the API client.
   - Submit a job to `/jobs` and view the response.
   - Poll for job completion.

Customize the payload in the notebook before submitting if you need different job parameters.

# API 

This note summarizes the api routes and how to call them with API keys. Callers must send a `Bearer` token.


## Job Lifecycle Summary

- `POST /jobs`: create a job document. The backend stamps `status="created"`, stores sheet metadata, and asynchronously starts verification.
- `POST /jobs/{job_id}/run`: for jobs marked `verified`, this triggers execution to move the job into processing and delegate work to the cloud runner.
- `GET /jobs/{job_id}` and `GET /jobs`: poll for status changes (`processing`, `completed`, `failed`, etc.), review errors, or surface the `cost_usd` estimate.
- `DELETE /jobs/{job_id}`: once finished—or if you abandon work—delete non-running jobs to keep the list tidy.

Alternatively you can use

- `POST /jobs/create-and-run`: Combined create + execute flow. This can be dangerous if you want to confirm the cost of the job.

## Job payload

A summary of the job_payload

```python
job_payload = {
    "client_sheet_link": SHEET_LINK,
    "name": "The name of the job",
    "scope": "This helps the AI understand the context of the categorisation. It can be helpful to give examples of categories. The more precise you are, the more likely you will get good results.",
    "job_type": "catify",  # catify|generate_categories|categorise
    "categorisation_model_level": "normal",  # normal|economy
    "data_column": "The column with your data",
    "response_column": "The new column you want to create",  # Only for catify|categorise
    "worksheet_name": "The worksheet to enter categories into",  # Optional for catify, required for generate_categories
    "num_categories": 5,  # Only for catify or generate_categories
    "overwrite": False  # If you want to be able to overwrite columns that are already there
}
```

## `/jobs` Endpoints

All endpoints below expect a valid `Authorization` header using one of the formats above. The router is registered under the `/jobs` prefix.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/jobs/check-sheet-access` | Verify Google Sheet accessibility and write permissions. |
| `GET` | `/jobs/sheet-stats` | Fetch metadata, headers, and plan-specific row limits for a sheet. |
| `POST` | `/jobs` | Create a new job document and trigger verification. |
| `GET` | `/jobs/{job_id}` | Retrieve a single job and its derived budget flags. |
| `GET` | `/jobs` | List jobs for the authenticated user (newest first). |
| `PATCH` | `/jobs/{job_id}` | Update editable fields on a job while the status is `created`. |
| `POST` | `/jobs/{job_id}/validate` | Run schema validation on the job payload. |
| `GET` | `/jobs/{job_id}/price` | Return the job's recorded `cost_usd`. |
| `POST` | `/jobs/{job_id}/run` | Trigger execution for verified jobs after overspend checks. |
| `POST` | `/jobs/create-and-run` | Combined create + execute flow with inline polling for completion. |
| `DELETE` | `/jobs/{job_id}` | Delete a job that is not currently processing. |

## Endpoint Details

### `GET /jobs/check-sheet-access`
- **Inputs**: `sheet_url` (query, `HttpUrl`).
- **Response**: `SheetCheckResponse` (`accessible`, `message`, optional `error_details`, `can_write`).

### `GET /jobs/sheet-stats`
- **Inputs**: `sheet_url` (query), optional `worksheet_name` (query), optional `header_row` (query, default `1`).
- **Response**: `SheetStatsResponse` (`file_type`, `is_google_sheet`, row/column counts, headers, worksheet list, tier row limit flags).

### `POST /jobs`
- **Inputs**: JSON body `JobCreate` (sheet link, metadata, job type parameters).
- **Response**: `JobPublic` for the created job (includes status, timestamps, cost placeholder). Triggers verification asynchronously.

### `GET /jobs/{job_id}`
- **Inputs**: `job_id` (path).
- **Response**: `JobPublic` for the requested job, with insufficient-funds flagging applied when relevant.

### `GET /jobs`
- **Inputs**: optional `status` (query), `skip` (query, default `0`), `limit` (query, default `50`, max `100`).
- **Response**: Array of `JobPublic` ordered newest-first.

### `PATCH /jobs/{job_id}`
- **Inputs**: `job_id` (path); JSON body `JobUpdate` (partial fields). Allowed only while the job status is `created`.
- **Response**: Updated `JobPublic`.

### `POST /jobs/{job_id}/validate`
- **Inputs**: `job_id` (path).
- **Response**: `ValidationResponse` with `valid` flag and optional `errors` list describing unmet constraints.

### `GET /jobs/{job_id}/price`
- **Inputs**: `job_id` (path).
- **Response**: `PriceResponse` exposing the current `cost_usd` (nullable).

### `POST /jobs/{job_id}/run`
- **Inputs**: `job_id` (path). Requires job status `verified` and sufficient balance.
- **Response**: `SubmitResponse`. The implementation also returns a `correlation_id` field for tracing.

### `POST /jobs/create-and-run`
- **Inputs**: JSON body `JobCreate` (same shape as `POST /jobs`). Performs limit checks and immediate execution.
- **Response**: `JobExecutionResult` conveying completion, failure, or timeout status plus optional sheet link or error details.

### `DELETE /jobs/{job_id}`
- **Inputs**: `job_id` (path). Fails for jobs still `processing`/`running`/`queued`.
- **Response**: `204 No Content` on successful deletion.

## `JobPublic` Schema

All routes that return job records share the `JobPublic` model. Key fields are:

- `id`: Firestore document ID.
- `name`, `scope`: Free-text job metadata supplied at creation.
- `job_type`: One of `catify`, `categorise`, `generate_categories`.
- `data_column`, `response_column`, `worksheet_name`, `num_categories`: Spreadsheet configuration parameters.
- `categorisation_model_level`: `advanced`, `normal`, or `economy`.
- `first_row_is_header`, `overwrite`: Boolean flags mirroring client options.
- `status`: Current lifecycle state (`created`, `verified`, `processing`, `completed`, `failed`, etc.).
- `cost_usd`: Latest cost estimate (float, nullable).
- `progress_pct`: Integer progress indicator.
- `client_sheet_link`: Echo of the sheet link when stored.
- `error`: Optional error messaging when the run is blocked or fails.
- `created_at`, `updated_at`: UTC timestamps.

## Example Request

```
curl \
  -H "Authorization: Bearer cat_XXXXXXXXXXXXXXXX" \
  -H "Content-Type: application/json" \
  https://{your-domain}/jobs
```

Replace the placeholder token with an API key generated under your account. The same header works for every `/jobs` route.


