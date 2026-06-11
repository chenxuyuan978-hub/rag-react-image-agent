import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.experiments.comparison_runner import (  # noqa: E402
    load_comparison_config,
    run_comparison,
)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the comparison experiment script."""
    parser = argparse.ArgumentParser(description="Run a comparison experiment.")
    parser.add_argument("config_path", help="Path to the comparison YAML config.")
    return parser.parse_args()


def main() -> int:
    """Load a comparison config, run it, and print result paths."""
    args = parse_args()

    try:
        config = load_comparison_config(args.config_path)
        result = run_comparison(config)
    except FileNotFoundError as error:
        print(f"File not found: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Comparison failed: {error}", file=sys.stderr)
        return 1

    print(f"comparison_name: {result['comparison_name']}")
    print(f"output_dir: {result['output_dir']}")
    print(f"metrics_path: {result['metrics_path']}")
    print(f"summary_path: {result['summary_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
