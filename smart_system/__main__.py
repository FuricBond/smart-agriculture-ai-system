"""
Entry point for running the Smart Agriculture System as a module.

Usage
-----
    cd C:\\CropProject

    python -m smart_system               # Interactive prediction mode
    python -m smart_system --evaluate    # Automated evaluation mode
    python -m smart_system --version     # Show version

Author  : Smart Agriculture AI Team
Version : 2.0.0
"""

import sys


def _main() -> None:
    """Parse arguments and route to appropriate mode."""
    args = sys.argv[1:]

    if '--evaluate' in args or '-e' in args:
        from smart_system.evaluation import main as eval_main
        eval_main()

    elif '--version' in args or '-v' in args:
        from smart_system import __version__
        from smart_system import config
        print(f"{config.SYSTEM_NAME}")
        print(f"Version: {__version__}")
        print(f"{config.SYSTEM_SUBTITLE}")

    elif '--help' in args or '-h' in args:
        print("Smart Agriculture System")
        print()
        print("Usage:")
        print("  python -m smart_system              Interactive mode")
        print("  python -m smart_system --evaluate    Automated evaluation")
        print("  python -m smart_system --version     Show version")
        print("  python -m smart_system --help        Show this help")

    else:
        from smart_system.smart_predict import main
        main()


if __name__ == "__main__":
    _main()
