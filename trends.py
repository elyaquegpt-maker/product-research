#!/usr/bin/env python3
"""Compare two research.py snapshots: best-seller climbers, new launches, price and stock changes.

Standard library only. See README.md for usage.
"""

import argparse
import csv
import html
import json
import sys
from datetime import date
from pathlib import Path

# A product counts as climbing/falling when its best-seller rank moves at least this many places.
RANK_MOVE_MIN = 5
PRICE_CHANGE_MIN = 0.05  # 5%

# Signals in report order, with a short explanation for the HTML report.
SIGNALS = [
    ("new_bestseller", "New in best-sellers", "Was unranked, now in the best-seller list"),
    ("climbing", "Climbing", f"Best-seller rank up {RANK_MOVE_MIN}+ places"),
    ("new_launch", "New launch", "Product didn't exist in the earlier snapshot"),
    ("price_up", "Price up", f"Price raised {PRICE_CHANGE_MIN:.0%}+ (often a sign of demand)"),
    ("price_down", "Price down", f"Price cut {PRICE_CHANGE_MIN:.0%}+ (discount or clearance)"),
    ("restocked", "Back in stock", "Was sold out, now available"),
    ("sold_out", "Sold out", "Was available, now sold out"),
    ("falling", "Falling", f"Best-seller rank down {RANK_MOVE_MIN}+ places"),
    ("dropped_bestseller", "Left best-sellers", "Was ranked, now unranked"),
    ("removed", "Removed", "Product no longer in the catalog"),
]
SIGNAL_LABEL = {key: label for key, label, _ in SIGNALS}
SIGNAL_ORDER = {key: i for i, (key, _, _) in enumerate(SIGNALS)}


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def list_snapshots(snapshot_dir):
    snaps = []
    for p in Path(snapshot_dir).glob("*.json"):
        try:
            snaps.append((date.fromisoformat(p.stem), p))
        except ValueError:
            continue
    return sorted(snaps)


def pick_snapshots(snaps, new_date=None, old_date=None, days=None):
    """Return (old_path, new_path). Default: newest snapshot vs the one before it."""
    by_date = dict(snaps)
    if new_date:
        if new_date not in by_date:
            raise SystemExit(f"No snapshot for {new_date}")
        new_d = new_date
    else:
        new_d = snaps[-1][0]
    older = [d for d, _ in snaps if d < new_d]
    if old_date:
        if old_date not in by_date:
            raise SystemExit(f"No snapshot for {old_date}")
        old_d = old_date
    elif days is not None:
        candidates = [d for d in older if (new_d - d).days >= days]
        if not candidates:
            raise SystemExit(f"No snapshot at least {days} days older than {new_d}")
        old_d = candidates[-1]
    else:
        if not older:
            raise SystemExit(f"Need two snapshots to compare; only found {new_d}. Run research.py again on another day.")
        old_d = older[-1]
    return by_date[old_d], by_date[new_d]


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    products = {(p["store"], p["handle"]): p for p in data["products"]}
    return data, products


def pct_change(old, new):
    if old in (None, 0) or new is None:
        return None
    return (new - old) / old


def compare(old_data, old_products, new_data, new_products):
    """Return one row per product with at least one signal, plus the stores that were skipped."""
    common = set(old_data["stores"]) & set(new_data["stores"])
    skipped = sorted(set(old_data["stores"]) ^ set(new_data["stores"]))
    rows = []
    for key in sorted(set(old_products) | set(new_products)):
        if key[0] not in common:
            continue
        old, new = old_products.get(key), new_products.get(key)
        p = new or old
        signals = []
        rank_old = old.get("bestseller_rank") if old else None
        rank_new = new.get("bestseller_rank") if new else None
        rank_change = rank_old - rank_new if rank_old and rank_new else None  # positive = moved up
        price_old = old.get("price") if old else None
        price_new = new.get("price") if new else None
        price_pct = pct_change(price_old, price_new)

        if old is None:
            signals.append("new_launch")
            if rank_new:
                signals.append("new_bestseller")
        elif new is None:
            signals.append("removed")
        else:
            if rank_new and not rank_old:
                signals.append("new_bestseller")
            elif rank_old and not rank_new:
                signals.append("dropped_bestseller")
            elif rank_change is not None and rank_change >= RANK_MOVE_MIN:
                signals.append("climbing")
            elif rank_change is not None and rank_change <= -RANK_MOVE_MIN:
                signals.append("falling")
            if price_pct is not None and price_pct >= PRICE_CHANGE_MIN:
                signals.append("price_up")
            elif price_pct is not None and price_pct <= -PRICE_CHANGE_MIN:
                signals.append("price_down")
            if new.get("available") and not old.get("available"):
                signals.append("restocked")
            elif old.get("available") and not new.get("available"):
                signals.append("sold_out")
        if not signals:
            continue
        signals.sort(key=SIGNAL_ORDER.get)
        rows.append({
            "signal": signals[0],
            "signals": signals,
            "store": key[0],
            "handle": key[1],
            "title": p.get("title", key[1]),
            "rank_old": rank_old,
            "rank_new": rank_new,
            "rank_change": rank_change,
            "price_old": price_old,
            "price_new": price_new,
            "price_change_pct": price_pct,
            "score": new.get("score") if new else None,
            "url": p.get("url", ""),
            "image": p.get("image", ""),
        })
    rows.sort(key=lambda r: (
        SIGNAL_ORDER[r["signal"]],
        r["rank_new"] or 10**9 if r["signal"] in ("new_bestseller", "new_launch") else 0,
        -(abs(r["rank_change"] or 0)),
        -(abs(r["price_change_pct"] or 0)),
        -(r["score"] or 0),
        r["store"], r["title"],
    ))
    return rows, skipped


CSV_FIELDS = [
    "signal", "signals", "store", "handle", "title", "rank_old", "rank_new", "rank_change",
    "price_old", "price_new", "price_change_pct", "score", "url", "image",
]


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CSV_FIELDS)
        for r in rows:
            out = []
            for k in CSV_FIELDS:
                v = r[k]
                if k == "signals":
                    v = ";".join(v)
                elif k == "price_change_pct" and v is not None:
                    v = f"{v * 100:.1f}"
                elif k == "score" and v is not None:
                    v = f"{v:.1f}"
                elif v is None:
                    v = ""
                out.append(v)
            w.writerow(out)


def describe(r):
    parts = []
    if r["rank_old"] or r["rank_new"]:
        parts.append(f"best-seller #{r['rank_old'] or '–'} → #{r['rank_new'] or '–'}")
    if r["price_old"] is not None and r["price_new"] is not None and r["price_old"] != r["price_new"]:
        parts.append(f"${r['price_old']:.2f} → ${r['price_new']:.2f}")
    elif (r["price_new"] or r["price_old"]) is not None:
        parts.append(f"${r['price_new'] if r['price_new'] is not None else r['price_old']:.2f}")
    return " · ".join(parts)


def write_html(rows, path, old_label, new_label, skipped, per_signal):
    e = html.escape
    sections = []
    for key, label, explain in SIGNALS:
        group = [r for r in rows if r["signal"] == key]
        if not group:
            continue
        items = []
        for r in group[:per_signal]:
            img = f'<img src="{e(r["image"])}" alt="" loading="lazy">' if r["image"] else '<div class="noimg"></div>'
            extra = ", ".join(SIGNAL_LABEL[s] for s in r["signals"][1:])
            items.append(
                f'<li><a href="{e(r["url"])}" target="_blank" rel="noopener">{img}</a><div>'
                f'<a class="t" href="{e(r["url"])}" target="_blank" rel="noopener">{e(r["title"])}</a>'
                f'<p>{e(r["store"])} · {e(describe(r))}</p>'
                + (f'<p class="x">also: {e(extra)}</p>' if extra else "") + "</div></li>"
            )
        more = f'<p class="more">+{len(group) - per_signal} more in trends.csv</p>' if len(group) > per_signal else ""
        sections.append(
            f'<section><h2>{e(label)} <span>{len(group)}</span></h2><p class="ex">{e(explain)}</p>'
            f'<ul>{"".join(items)}</ul>{more}</section>'
        )
    note = f"<p>Skipped (missing from one snapshot): {e(', '.join(skipped))}</p>" if skipped else ""
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Store Trends</title>
<style>
:root {{ --bg:#f6f6f4; --card:#fff; --text:#1d1d1b; --muted:#6b6b66; --line:#e3e3de; --accent:#2f6f4f; --track:#ecece7; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#161615; --card:#21211f; --text:#ececea; --muted:#a2a29c; --line:#34342f; --accent:#6cc497; --track:#2e2e2a; }}
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:14px/1.45 system-ui, -apple-system, Segoe UI, sans-serif; }}
.wrap {{ max-width:1100px; margin:0 auto; padding:24px 16px; }}
h1 {{ margin:0 0 4px; font-size:22px; }}
header p, .ex, .more {{ color:var(--muted); margin:2px 0; }}
section {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px 16px; margin-top:16px; }}
h2 {{ font-size:16px; margin:0; }}
h2 span {{ color:var(--accent); }}
ul {{ list-style:none; padding:0; margin:10px 0 0; display:grid; grid-template-columns:repeat(auto-fill, minmax(300px, 1fr)); gap:10px; }}
li {{ display:flex; gap:10px; align-items:center; min-width:0; }}
li img, .noimg {{ width:56px; height:56px; object-fit:cover; border-radius:6px; background:var(--track); flex:none; display:block; }}
li div {{ min-width:0; }}
li p {{ margin:0; color:var(--muted); font-size:12px; }}
.t {{ color:inherit; text-decoration:none; font-weight:600; display:block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.t:hover {{ text-decoration:underline; }}
.x {{ color:var(--accent); }}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>Store Trends</h1>
  <p>{e(old_label)} → {e(new_label)} · {len(rows)} products changed.</p>
  {note}
</header>
{"".join(sections) or "<p>No changes between these snapshots.</p>"}
</div>
</body>
</html>
"""
    Path(path).write_text(page, encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--snapshot-dir", default="snapshots", help="where research.py saved its snapshots")
    ap.add_argument("--out-dir", default="output", help="where to write trends.csv and trends.html")
    ap.add_argument("--days", type=int, help="compare against the newest snapshot at least N days older")
    ap.add_argument("--old", type=date.fromisoformat, help="earlier snapshot date (YYYY-MM-DD)")
    ap.add_argument("--new", type=date.fromisoformat, help="later snapshot date (default: newest)")
    ap.add_argument("--per-signal", type=int, default=30, help="products per section in the HTML report")
    args = ap.parse_args(argv)

    snaps = list_snapshots(args.snapshot_dir)
    if not snaps:
        log(f"No snapshots in {args.snapshot_dir}/. Run research.py first.")
        return 1
    old_path, new_path = pick_snapshots(snaps, args.new, args.old, args.days)
    old_data, old_products = load(old_path)
    new_data, new_products = load(new_path)
    rows, skipped = compare(old_data, old_products, new_data, new_products)
    if skipped:
        log(f"Skipping stores missing from one snapshot: {', '.join(skipped)}")

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    write_csv(rows, out / "trends.csv")
    write_html(rows, out / "trends.html", old_path.stem, new_path.stem, skipped, args.per_signal)
    log(f"Compared {old_path.stem} → {new_path.stem}: {len(rows)} products changed. "
        f"Wrote {out / 'trends.csv'} and {out / 'trends.html'}")

    for key, label, _ in SIGNALS:
        group = [r for r in rows if r["signal"] == key]
        if not group:
            continue
        print(f"\n{label} ({len(group)})")
        for r in group[:5]:
            print(f"  {r['store']:<22} {r['title'][:45]:<45}  {describe(r)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
