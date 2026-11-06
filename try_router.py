"""Default interactive entry point for light_decider."""

from light_decider.predict import DEFAULT_MODEL_PATH
from try_router_semantic import main as run_interactive


def main() -> None:
    run_interactive(default_model=DEFAULT_MODEL_PATH)


if __name__ == "__main__":
    main()
