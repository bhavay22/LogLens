# LogLens AI 🔍

AI-powered log analysis for data engineering pipelines.

LogLens analyzes Spark, Airflow, and application logs and automatically identifies:

- Root cause
- Failure category
- Severity
- Suggested remediation
- Confidence score

## Example

Input:

    ExecutorLostFailure:
    Container killed by YARN for exceeding memory limits.

LogLens:

    Category      : OOM
    Severity      : HIGH
    Root Cause    : The process exceeded its available memory limit.
    Confidence    : 0.94
    Suggested Fix : Increase executor/worker memory, reduce partition size,
                    or optimize the operation causing high memory usage.

## Supported Categories

| Category | Description |
|----------|-------------|
| OOM | Memory-related failures |
| NETWORK | Connectivity and timeout failures |
| SQL | SQL syntax/schema failures |
| PERMISSION | IAM/access failures |
| DATA_QUALITY | Invalid or unexpected data |
| CONFIGURATION | Configuration problems |
| UNKNOWN | Unclassified failures |

## Installation

```bash
git clone https://github.com/<your-username>/loglens-ai.git

cd loglens-ai

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
