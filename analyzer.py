import json
import os
import re

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


SYSTEM_PROMPT = """
You are an expert Data Engineering incident analyzer.

Analyze the provided application, Spark, Airflow, or data pipeline logs.

Return ONLY valid JSON with this structure:

{
  "category": "OOM|NETWORK|SQL|PERMISSION|DATA_QUALITY|CONFIGURATION|UNKNOWN",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "root_cause": "short explanation",
  "suggested_fix": "practical remediation",
  "confidence": 0.0
}

Do not include markdown.
"""


def analyze_with_llm(log_text):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or OpenAI is None:
        return None

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": log_text[-12000:]
            }
        ]
    )

    content = response.choices[0].message.content

    return json.loads(content)


def analyze_with_rules(log_text):
    text = log_text.lower()

    patterns = [
        (
            ["outofmemory", "out of memory", "exceeding memory",
             "memory limit", "oom"],
            {
                "category": "OOM",
                "severity": "HIGH",
                "root_cause": "The process exceeded its available memory limit.",
                "suggested_fix": (
                    "Increase executor/worker memory, reduce partition size, "
                    "or optimize the operation causing high memory usage."
                ),
                "confidence": 0.94
            }
        ),
        (
            ["permission denied", "accessdenied", "access denied",
             "unauthorized", "forbidden"],
            {
                "category": "PERMISSION",
                "severity": "HIGH",
                "root_cause": "The workload does not have sufficient permissions.",
                "suggested_fix": (
                    "Check IAM/role permissions and verify access to the "
                    "target resource."
                ),
                "confidence": 0.95
            }
        ),
        (
            ["timeout", "timed out", "connection refused",
             "connection reset", "network"],
            {
                "category": "NETWORK",
                "severity": "HIGH",
                "root_cause": "The workload encountered a network or connectivity failure.",
                "suggested_fix": (
                    "Check network connectivity, service availability, "
                    "timeouts, security groups, and retry configuration."
                ),
                "confidence": 0.90
            }
        ),
        (
            ["syntax error", "sql error", "sqlstate", "column not found",
             "table not found", "ambiguous column"],
            {
                "category": "SQL",
                "severity": "MEDIUM",
                "root_cause": "The SQL query contains an invalid reference or syntax.",
                "suggested_fix": (
                    "Validate the SQL syntax and verify table and column "
                    "names against the current schema."
                ),
                "confidence": 0.91
            }
        ),
        (
            ["null value", "duplicate", "schema mismatch",
             "invalid record", "data quality"],
            {
                "category": "DATA_QUALITY",
                "severity": "MEDIUM",
                "root_cause": "The pipeline detected an unexpected data-quality condition.",
                "suggested_fix": (
                    "Validate incoming data, enforce schema checks, "
                    "and quarantine invalid records."
                ),
                "confidence": 0.87
            }
        ),
    ]

    for keywords, result in patterns:
        if any(keyword in text for keyword in keywords):
            return result

    return {
        "category": "UNKNOWN",
        "severity": "MEDIUM",
        "root_cause": "Unable to determine the root cause from the available log.",
        "suggested_fix": (
            "Review the surrounding logs and provide more context "
            "for deeper analysis."
        ),
        "confidence": 0.35
    }


def analyze_log(log_text):
    """
    Try LLM analysis first.
    Fall back to deterministic rules if an API is unavailable.
    """

    try:
        result = analyze_with_llm(log_text)

        if result:
            return result

    except Exception as exc:
        print(f"LLM analysis unavailable, using fallback: {exc}")

    return analyze_with_rules(log_text)
