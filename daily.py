#!/usr/bin/env python3
"""Daily run: research.py, then trends.py and profit.py when they have what they need.

Meant for cron or Windows Task Scheduler. Works from any current directory, and logs each run
to logs/YYYY-MM-DD.log. Standard library only.
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, help="trends.py: compare against a snapshot at least N days older")
    ap.add_argument("--cost-pct", type=float, help="profit.py: estimate missing costs as this percent of price")
    args = ap.parse_args(argv)

    log_dir = HERE / "logs"
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / f"{datetime.now():%Y-%m-%d}.log"

    with open(log_path, "a", encoding="utf-8") as log_file:
        def say(msg):
            print(msg, flush=True)
            log_file.write(msg + "\n")
            log_file.flush()

        def run(script, *extra):
            say(f"\n=== {script} {' '.join(extra)}".rstrip())
            proc = subprocess.Popen(
                [sys.executable, str(HERE / script), *extra], cwd=HERE,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
            )
            for line in proc.stdout:
                say(line.rstrip("\n"))
            return proc.wait()

        say(f"##### Daily run {datetime.now():%Y-%m-%d %H:%M:%S}")
        if run("research.py") != 0:
            say("\nresearch.py failed; skipping trends and profit.")
            return 1

        status = 0
        if len(list((HERE / "snapshots").glob("*.json"))) >= 2:
            status |= run("trends.py", *(["--days", str(args.days)] if args.days is not None else []))
        else:
            say("\n=== trends.py skipped: needs snapshots from two different days (run again tomorrow)")

        if (HERE / "costs.csv").exists() or args.cost_pct is not None:
            status |= run("profit.py", *(["--cost-pct", str(args.cost_pct)] if args.cost_pct is not None else []))
        else:
            say("\n=== profit.py skipped: no costs.csv (or pass --cost-pct to estimate)")

        say(f"\n##### Done {datetime.now():%H:%M:%S}. Reports in {HERE / 'output'}; log in {log_path}")
        return 1 if status else 0


if __name__ == "__main__":
    sys.exit(main())
