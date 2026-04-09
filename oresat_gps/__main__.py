"""Main entry point."""

import sys

from . import main

rc = 1
try:
    main()
    rc = 0
except (ValueError, OSError) as e:
    print("Error:", e, file=sys.stderr)  # noqa: T201
sys.exit(rc)
