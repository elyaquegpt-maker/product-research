#!/usr/bin/env python3
"""Daily run: research.py, then trends.py and profit.py when they have what they need.

Meant for cron or Windows Task Scheduler. Works from any current directory, and logs each run
to logs/YYYY-MM-DD.log. Standard library only.
"""

import argparse
import subprocess
import sys
import threading
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, help="trends.py: compare against a snapshot at least N days older")
    ap.add_argument("--cost-pct", type=float, help="profit.py: estimate missing costs as this percent of price")
    ap.add_argument("--keep-days", type=int, help="delete snapshots older than this many days (default: keep all)")
    ap.add_argument("--summary", help="also write each step's results (no progress lines) to this Markdown file")
    args = ap.parse_args(argv)
    summary = []

    log_dir = HERE / "logs"
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / f"{datetime.now():%Y-%m-%d}.log"

    lock = threading.Lock()
    with open(log_path, "a", encoding="utf-8") as log_file:
        def say(msg):
            with lock:
                print(msg, flush=True)
                log_file.write(msg + "\n")
                log_file.flush()

        def run(script, *extra):
            say(f"\n=== {script} {' '.join(extra)}".rstrip())
            proc = subprocess.Popen(
                [sys.executable, str(HERE / script), *extra], cwd=HERE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
            )
            results, progress = [], []  # stdout carries each script's results; stderr its progress messages

            def pump(stream, keep):
                for line in stream:
                    say(line.rstrip("\n"))
                    keep.append(line.rstrip("\n"))

            reader = threading.Thread(target=pump, args=(proc.stderr, progress))
            reader.start()
            pump(proc.stdout, results)
            reader.join()
            code = proc.wait()
            if code:  # show why it failed
                results = progress[-15:] + results
            body = "\n".join(results).strip() or "(no results)"
            summary.append(f"### {script}{' (failed)' if code else ''}\n\n```\n{body}\n```\n")
            return code

        say(f"##### Daily run {datetime.now():%Y-%m-%d %H:%M:%S}")
        if args.keep_days is not None:
            cutoff = date.today() - timedelta(days=args.keep_days)
            for snap in sorted((HERE / "snapshots").glob("*.json")):
                try:
                    old = date.fromisoformat(snap.stem) < cutoff
                except ValueError:
                    continue
                if old:
                    snap.unlink()
                    say(f"Deleted old snapshot {snap.name}")
        if run("research.py") != 0:
            say("\nresearch.py failed; skipping trends and profit.")
            if args.summary:
                Path(args.summary).write_text("\n".join(summary), encoding="utf-8")
            return 1

        status = 0
        if len(list((HERE / "snapshots").glob("*.json"))) >= 2:
            status |= run("trends.py", *(["--days", str(args.days)] if args.days is not None else []))
        else:
            say("\n=== trends.py skipped: needs snapshots from two different days (run again tomorrow)")
            summary.append("### trends.py\n\nSkipped: needs snapshots from two different days.\n")

        if (HERE / "costs.csv").exists() or args.cost_pct is not None:
            status |= run("profit.py", *(["--cost-pct", str(args.cost_pct)] if args.cost_pct is not None else []))
        else:
            say("\n=== profit.py skipped: no costs.csv (or pass --cost-pct to estimate)")
            summary.append("### profit.py\n\nSkipped: no costs.csv (or pass --cost-pct to estimate).\n")

        if args.summary:
            Path(args.summary).write_text(
                f"## Product research {date.today()}\n\n" + "\n".join(summary), encoding="utf-8")
        say(f"\n##### Done {datetime.now():%H:%M:%S}. Reports in {HERE / 'output'}; log in {log_path}")
        return 1 if status else 0


if __name__ == "__main__":
    sys.exit(main())
