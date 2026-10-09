#!/usr/bin/env python3
"""Break-even ROAS per product: can this product make money with paid ads?

Reads research.py's ranked CSV plus costs.csv, and writes output/profit.csv. Standard library only.

Per order, before ad spend:
    profit = price × (1 − return rate) − cost − shipping − payment fees
Returned orders are refunded in full and the item is written off (typical for dropshipping);
payment fees aren't refunded.
    break-even ROAS = price / profit      (ad platforms report ROAS on gross revenue)
    max CPA         = profit              (most you can pay in ads per order and break even)
    target ROAS     = price / (profit − target margin × price)
"""

import argparse
import csv
import sys
from pathlib import Path

from research import log, lookup_cost, read_costs

# Verdict by break-even ROAS. Cold Meta traffic often runs around 1.5-3x, so below 2 leaves room.
VERDICTS = [(1.5, "great"), (2.0, "good"), (3.0, "risky")]
VERDICT_ORDER = {"great": 0, "good": 1, "risky": 2, "avoid": 3}


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def economics(price, cost, shipping, fee_pct, fee_fixed, return_rate, target_margin):
    fees = price * fee_pct + fee_fixed
    return_loss = price * return_rate
    profit = price - return_loss - cost - shipping - fees
    be_roas = price / profit if profit > 0 else None
    target_profit = profit - target_margin * price
    target_roas = price / target_profit if target_profit > 0 else None
    verdict = "avoid"
    if be_roas is not None:
        verdict = next((v for limit, v in VERDICTS if be_roas <= limit), "avoid")
    return {
        "fees": fees,
        "return_loss": return_loss,
        "profit": profit,
        "profit_pct": profit / price,
        "break_even_roas": be_roas,
        "max_cpa": max(profit, 0.0),
        "target_roas": target_roas,
        "verdict": verdict,
    }


CSV_FIELDS = [
    "verdict", "break_even_roas", "target_roas", "max_cpa", "profit", "profit_pct", "score",
    "store", "handle", "title", "price", "cost", "cost_source", "shipping", "fees", "return_loss", "url",
]


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CSV_FIELDS)
        for r in rows:
            out = []
            for k in CSV_FIELDS:
                v = r[k]
                if v is None:
                    v = ""
                elif k == "profit_pct":
                    v = f"{v * 100:.1f}"
                elif isinstance(v, float):
                    v = f"{v:.2f}"
                out.append(v)
            w.writerow(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ranked", default="output/products_ranked.csv", help="research.py output")
    ap.add_argument("--costs", default="costs.csv", help="CSV with handle,cost[,shipping,store]")
    ap.add_argument("--out", default="output/profit.csv", help="where to write the results")
    ap.add_argument("--shipping", type=float, default=0.0,
                    help="shipping per order when costs.csv has none (default 0: assume it's in the cost)")
    ap.add_argument("--fee-pct", type=float, default=2.9, help="payment fee, percent of price (default 2.9)")
    ap.add_argument("--fee-fixed", type=float, default=0.30, help="payment fee per order (default 0.30)")
    ap.add_argument("--return-rate", type=float, default=10.0, help="percent of orders refunded (default 10)")
    ap.add_argument("--target-margin", type=float, default=15.0,
                    help="net profit margin wanted after ads, percent of price (default 15)")
    ap.add_argument("--cost-pct", type=float,
                    help="estimate missing costs as this percent of price (rows marked 'estimate')")
    args = ap.parse_args(argv)

    if not Path(args.ranked).exists():
        log(f"{args.ranked} not found. Run research.py first.")
        return 1
    costs = read_costs(args.costs)
    if not costs and args.cost_pct is None:
        log(f"No costs in {args.costs}. Add costs.csv (see README) or pass --cost-pct to estimate.")
        return 1

    rows, missing = [], 0
    with open(args.ranked, newline="", encoding="utf-8") as f:
        for p in csv.DictReader(f):
            price = to_float(p.get("price"))
            if not price:
                continue
            entry = lookup_cost(costs, p["store"], p["handle"])
            if entry:
                cost, source = entry["cost"], "costs.csv"
                shipping = entry["shipping"] if entry["shipping"] is not None else args.shipping
            elif args.cost_pct is not None:
                cost, source, shipping = price * args.cost_pct / 100, "estimate", args.shipping
            else:
                missing += 1
                continue
            row = {k: p.get(k, "") for k in ("store", "handle", "title", "url")}
            row.update(price=price, cost=cost, cost_source=source, shipping=shipping, score=to_float(p.get("score")))
            row.update(economics(price, cost, shipping, args.fee_pct / 100, args.fee_fixed,
                                 args.return_rate / 100, args.target_margin / 100))
            rows.append(row)

    rows.sort(key=lambda r: (VERDICT_ORDER[r["verdict"]], -(r["score"] or 0), r["break_even_roas"] or 1e9))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_csv(rows, out)

    log(f"Assumptions: fees {args.fee_pct}% + ${args.fee_fixed:.2f}, returns {args.return_rate}%, "
        f"default shipping ${args.shipping:.2f}, target margin {args.target_margin}%")
    if missing:
        log(f"{missing} products skipped: no cost in {args.costs} (use --cost-pct to estimate)")
    counts = {v: sum(r["verdict"] == v for r in rows) for v in VERDICT_ORDER}
    log(f"Wrote {out}: " + ", ".join(f"{n} {v}" for v, n in counts.items()))

    print(f"\n{'verdict':<7} {'BE ROAS':>7} {'max CPA':>8} {'profit':>7} {'price':>8} {'score':>5}  {'store':<22} title")
    for r in rows[:15]:
        be = f"{r['break_even_roas']:.2f}" if r["break_even_roas"] else "never"
        print(f"{r['verdict']:<7} {be:>7} {r['max_cpa']:>8.2f} {r['profit']:>7.2f} {r['price']:>8.2f} "
              f"{r['score'] or 0:>5.1f}  {r['store']:<22} {r['title'][:40]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
