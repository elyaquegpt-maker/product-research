#!/usr/bin/env python3
"""Profit per Etsy sale for Printify products, with and without ads.

Writes output/etsy_printify.csv and prints a table. Standard library only.

Etsy fees (US, 2026), on an order where shipping is built into the price ("free shipping"):
    listing      $0.20 per sale (each sale auto-renews the listing)
    transaction  6.5% of the order total
    processing   3% + $0.25 of the order total
    offsite ads  15% of the order total, only on sales Etsy attributes to its offsite ads

Base costs are Printify "from" prices (cheapest provider, standard size) as listed in 2026.
Shipping is an estimate for one item to a US address; check your provider before pricing.
"""

import argparse
import csv
from pathlib import Path

LISTING_FEE = 0.20
TRANSACTION_PCT = 0.065
PROCESSING_PCT = 0.03
PROCESSING_FIXED = 0.25
OFFSITE_ADS_PCT = 0.15
PREMIUM_DISCOUNT = 0.20  # Printify Premium: up to 20% off most products

# name, retail price, Printify base (Free plan), estimated US shipping
PRODUCTS = [
    ("T-shirt (Bella+Canvas 3001)", 27.99, 10.98, 4.75),
    ("T-shirt (Comfort Colors 1717)", 32.99, 12.65, 4.75),
    ("Crewneck sweatshirt (Gildan 18000)", 42.99, 17.87, 8.49),
    ("Embroidered dad hat", 29.99, 12.95, 5.00),
    ("Mug 11oz", 19.99, 5.02, 7.50),
    ("Poster 12x18 (matte)", 24.99, 8.50, 5.50),
    ("Poster 18x24 (matte)", 34.99, 12.00, 6.50),
    ("Kiss-cut sticker 3x3", 4.99, 1.21, 4.00),
    ("Ceramic ornament", 18.99, 4.93, 4.50),
    ("Desk mat", 32.99, 10.67, 6.50),
    ("Tumbler 20oz (stainless)", 34.99, 21.79, 7.50),
    ("Sherpa fleece blanket 50x60", 54.99, 24.79, 10.00),
    ("Framed poster (small, Roma Imaging)", 69.99, 35.89, 9.00),
]


def etsy_fees(price, offsite=False):
    fees = LISTING_FEE + price * (TRANSACTION_PCT + PROCESSING_PCT) + PROCESSING_FIXED
    if offsite:
        fees += price * OFFSITE_ADS_PCT
    return fees


def row(name, price, base, shipping, premium):
    if premium:
        base = round(base * (1 - PREMIUM_DISCOUNT), 2)
    cost = base + shipping
    profit = price - cost - etsy_fees(price)
    offsite_profit = price - cost - etsy_fees(price, offsite=True)
    # Etsy Ads ROAS is revenue / ad spend, so break-even ROAS = price / profit before ads.
    be_roas = price / profit if profit > 0 else None
    return {
        "product": name,
        "price": price,
        "base": base,
        "shipping": shipping,
        "etsy_fees": round(etsy_fees(price), 2),
        "profit": round(profit, 2),
        "margin_pct": round(100 * profit / price, 1),
        "profit_offsite_ad": round(offsite_profit, 2),
        "break_even_roas": round(be_roas, 2) if be_roas else "",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--premium", action="store_true", help="apply the Printify Premium discount")
    args = parser.parse_args()

    rows = [row(*p, premium=args.premium) for p in PRODUCTS]
    rows.sort(key=lambda r: r["profit"], reverse=True)

    out = Path(__file__).resolve().parent / "output"
    out.mkdir(exist_ok=True)
    with open(out / "etsy_printify.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print("| Product | Price | Base | Ship | Etsy fees | Profit | Margin | With offsite ad | Break-even ROAS |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        roas = f"{r['break_even_roas']}x" if r["break_even_roas"] else "never"
        print(f"| {r['product']} | ${r['price']:.2f} | ${r['base']:.2f} | ${r['shipping']:.2f} "
              f"| ${r['etsy_fees']:.2f} | ${r['profit']:.2f} | {r['margin_pct']}% "
              f"| ${r['profit_offsite_ad']:.2f} | {roas} |")


if __name__ == "__main__":
    main()
