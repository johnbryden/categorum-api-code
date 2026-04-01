# Categorum API 

This repository provides a minimal client for exercising the Categorum Jobs API.

## Contents

- `client_wrapper.py`: lightweight wrapper around the Jobs API using `requests`.
- `example_job_submission.ipynb`: notebook that submits and monitors a sample job.

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

2. Open `example_job_submission.ipynb` and enter your own SHEET_LINK. Run the cells in order to:
   - Load environment variables.
   - Instantiate the API client.
   - Submit a job to `/jobs` and view the response.
   - Poll for job completion.

Customize the payload in the notebook before submitting if you need different job parameters.

## API Documentation

See [API.md](API.md) for full API documentation.
