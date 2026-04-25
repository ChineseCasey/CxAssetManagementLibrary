from __future__ import annotations

import argparse
from pathlib import Path

from cxasset_api.sync_worker import run_full_sync


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full library sync (filesystem -> database).")
    parser.add_argument(
        "--roots",
        nargs="*",
        default=None,
        help="Optional library root directories. Defaults to CXASSET_LIBRARY_ROOTS.",
    )
    args = parser.parse_args()

    roots = [Path(item).resolve() for item in args.roots] if args.roots else None
    results = run_full_sync(roots)
    for item in results:
        print(
            f"[sync] library={item.library_name} "
            f"nodes={item.scanned_nodes} assets={item.scanned_assets} errors={item.error_count}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
