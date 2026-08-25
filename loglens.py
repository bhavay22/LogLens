import argparse
import json

from analyzer import analyze_log


def main():
    parser = argparse.ArgumentParser(
        description="LogLens AI - AI-powered log analyzer"
    )

    parser.add_argument(
        "logfile",
        help="Path to the log file"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON only"
    )

    args = parser.parse_args()

    with open(args.logfile, "r", encoding="utf-8") as f:
        log_text = f.read()

    result = analyze_log(log_text)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("\n=== LogLens AI ===\n")
    print(f"Category      : {result['category']}")
    print(f"Severity      : {result['severity']}")
    print(f"Root Cause    : {result['root_cause']}")
    print(f"Confidence    : {result['confidence']}")
    print(f"Suggested Fix : {result['suggested_fix']}")


if __name__ == "__main__":
    main()
