import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.experiments.config_schema import load_experiment_config
from app.experiments.experiment_runner import run_experiment


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the demo experiment script."""
    parser = argparse.ArgumentParser(description="Run a configured demo experiment.")
    parser.add_argument("config_path", help="Path to the experiment YAML config.")
    return parser.parse_args()


def main() -> int:
    """Load an experiment config, run it, and print result paths."""
    args = parse_args()

    try:
        config = load_experiment_config(args.config_path)
        result = run_experiment(config)
    except FileNotFoundError as error:
        print(f"File not found: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Experiment failed: {error}", file=sys.stderr)
        return 1

    print(f"output_dir: {result.output_dir}")
    print(f"metrics_path: {result.metrics_path}")
    print(f"summary_path: {result.summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
