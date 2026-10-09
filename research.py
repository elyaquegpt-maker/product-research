#!/usr/bin/env python3
"""Shopify product research: download catalogs, score products 0-100, write a ranked CSV and HTML report.

Standard library only. See README.md for usage and the scoring model.
"""

import argparse
import csv
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (compatible; product-research/1.0)"
PAGE_SIZE = 250

# Score weights (sum to 100).
W_BESTSELLER = 35.0
W_SIMILAR = 20.0
W_PRICE = 20.0
W_RECENT = 15.0
W_MARGIN = 10.0

PRICE_LOW, PRICE_HIGH = 25.0, 90.0
RECENT_FULL_DAYS, RECENT_ZERO_DAYS = 30, 365
SIMILAR_THRESHOLD = 0.4  # Jaccard similarity of title tokens
SIMILAR_FULL_STORES = 3  # this many other stores with a similar product = full points
MARGIN_FULL = 0.70  # 70%+ gross margin = full points

STOPWORDS = {
    "the", "and", "for", "with", "men", "mens", "women", "womens", "unisex", "kid", "kids",
    "new", "pack", "set", "size", "edition", "collection", "style", "classic",
}


class Fetcher:
    """HTTP GET with a fixed delay between requests and retries on throttling."""

    def __init__(self, delay=1.0, timeout=30, retries=3):
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self._last = 0.0

    def _wait(self):
        remaining = self.delay - (time.monotonic() - self._last)
        if remaining > 0:
            time.sleep(remaining)
        self._last = time.monotonic()

    def get(self, url):
        for attempt in range(1, self.retries + 1):
            self._wait()
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    charset = resp.headers.get_content_charset() or "utf-8"
                    return resp.read().decode(charset, errors="replace")
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < self.retries:
                    retry_after = e.headers.get("Retry-After", "")
                    wait = float(retry_after) if retry_after.isdigit() else 2.0 * attempt
                    log(f"  HTTP {e.code} for {url}, retrying in {wait:.0f}s")
                    time.sleep(wait)
                    continue
                raise
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                if attempt < self.retries:
                    log(f"  {e} for {url}, retrying")
                    time.sleep(2.0 * attempt)
                    continue
                raise
        raise RuntimeError("unreachable")


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def store_base(line):
    """'kith.com' -> 'https://kith.com'. Lines with an explicit scheme are kept as given."""
    line = line.strip().rstrip("/")
    if re.match(r"^https?://", line):
        return line
    return "https://" + line


def store_name(base):
    return re.sub(r"^https?://", "", base)


def read_stores(path):
    stores = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            stores.append(store_base(line))
    return stores


def fetch_products(fetcher, base, max_pages):
    products = []
    for page in range(1, max_pages + 1):
        data = json.loads(fetcher.get(f"{base}/products.json?limit={PAGE_SIZE}&page={page}"))
        batch = data.get("products", [])
        products.extend(batch)
        log(f"  products page {page}: {len(batch)}")
        if len(batch) < PAGE_SIZE:
            break
    return products


HANDLE_RE = re.compile(r"""/products/([A-Za-z0-9][A-Za-z0-9\-_.%]*)""")


def fetch_bestseller_order(fetcher, base, known_handles, max_pages):
    """Return product handles in best-selling order, scraped from the collection page HTML."""
    order, seen = [], set()
    for page in range(1, max_pages + 1):
        url = f"{base}/collections/all?sort_by=best-selling"
        if page > 1:
            url += f"&page={page}"
        page_html = fetcher.get(url)
        new = 0
        for m in HANDLE_RE.finditer(page_html):
            handle = m.group(1).lower().rstrip(".")
            if handle in known_handles and handle not in seen:
                seen.add(handle)
                order.append(handle)
                new += 1
        log(f"  best-seller page {page}: {new} new handles")
        if new == 0:
            break
    return order


def read_costs(path):
    """costs.csv columns: handle, cost, and optionally store (domain). Keys: (store, handle) and ('', handle)."""
    costs = {}
    if not path or not Path(path).exists():
        return costs
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
            handle, cost = row.get("handle", "").lower(), row.get("cost", "").lstrip("$")
            if not handle or not cost:
                continue
            try:
                value = float(cost)
            except ValueError:
                log(f"costs.csv: skipping bad cost {cost!r} for {handle}")
                continue
            store = store_name(store_base(row["store"])) if row.get("store") else ""
            costs[(store, handle)] = value
    return costs


def tokens(title):
    words = re.findall(r"[a-z]+", title.lower())
    out = set()
    for w in words:
        if len(w) < 3 or w in STOPWORDS:
            continue
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.add(w)
    return out


def parse_time(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def price_of(product):
    prices = []
    for v in product.get("variants") or []:
        try:
            prices.append(float(v.get("price")))
        except (TypeError, ValueError):
            pass
    return min(prices) if prices else None


def score_price(price):
    if price is None or price <= 0:
        return 0.0
    if PRICE_LOW <= price <= PRICE_HIGH:
        return W_PRICE
    if price < PRICE_LOW:
        return W_PRICE * price / PRICE_LOW
    return W_PRICE * max(0.0, 1 - (price - PRICE_HIGH) / PRICE_HIGH)


def score_recent(published, now):
    if published is None:
        return 0.0
    age = (now - published).days
    if age <= RECENT_FULL_DAYS:
        return W_RECENT
    if age >= RECENT_ZERO_DAYS:
        return 0.0
    return W_RECENT * (RECENT_ZERO_DAYS - age) / (RECENT_ZERO_DAYS - RECENT_FULL_DAYS)


def score_bestseller(rank, ranked_count):
    if rank is None or ranked_count == 0:
        return 0.0
    return W_BESTSELLER * (1 - (rank - 1) / ranked_count)


def similar_store_counts(rows):
    """For each row, the other stores that sell a product with a similar title."""
    index = defaultdict(list)  # token -> row indices
    for i, r in enumerate(rows):
        for t in r["_tokens"]:
            index[t].append(i)
    result = []
    for i, r in enumerate(rows):
        toks = r["_tokens"]
        matches = set()
        if toks:
            candidates = {j for t in toks for j in index[t] if rows[j]["store"] != r["store"]}
            for j in candidates:
                if rows[j]["store"] in matches:
                    continue
                other = rows[j]["_tokens"]
                if len(toks & other) / len(toks | other) >= SIMILAR_THRESHOLD:
                    matches.add(rows[j]["store"])
        result.append(sorted(matches))
    return result


def build_rows(store_data, costs, now):
    rows = []
    for base, (products, bestsellers) in store_data.items():
        store = store_name(base)
        rank_of = {h: i + 1 for i, h in enumerate(bestsellers)}
        for p in products:
            handle = (p.get("handle") or "").lower()
            price = price_of(p)
            images = p.get("images") or []
            published = parse_time(p.get("published_at") or p.get("created_at"))
            cost = costs.get((store, handle), costs.get(("", handle)))
            variants = p.get("variants") or []
            rows.append({
                "store": store,
                "handle": handle,
                "title": p.get("title") or handle,
                "vendor": p.get("vendor") or "",
                "product_type": p.get("product_type") or "",
                "price": price,
                "available": any(v.get("available") for v in variants),
                "published_at": published.date().isoformat() if published else "",
                "bestseller_rank": rank_of.get(handle),
                "url": f"{base}/products/{handle}",
                "image": images[0].get("src", "") if images else "",
                "cost": cost,
                "_published": published,
                "_ranked_count": len(bestsellers),
                "_tokens": tokens(p.get("title") or ""),
            })

    for r, similar in zip(rows, similar_store_counts(rows)):
        margin = (r["price"] - r["cost"]) / r["price"] if r["cost"] is not None and r["price"] else None
        r["similar_stores"] = similar
        r["margin"] = margin
        r["s_bestseller"] = score_bestseller(r["bestseller_rank"], r["_ranked_count"])
        r["s_similar"] = W_SIMILAR * min(len(similar), SIMILAR_FULL_STORES) / SIMILAR_FULL_STORES
        r["s_price"] = score_price(r["price"])
        r["s_recent"] = score_recent(r["_published"], now)
        r["s_margin"] = W_MARGIN * min(max(margin, 0.0) / MARGIN_FULL, 1.0) if margin is not None else 0.0
        r["score"] = r["s_bestseller"] + r["s_similar"] + r["s_price"] + r["s_recent"] + r["s_margin"]

    rows.sort(key=lambda r: (-r["score"], r["bestseller_rank"] or 10**9, r["store"], r["title"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    return rows


CSV_FIELDS = [
    "rank", "score", "store", "title", "vendor", "product_type", "price", "cost", "margin",
    "available", "published_at", "bestseller_rank", "similar_stores",
    "s_bestseller", "s_similar", "s_price", "s_recent", "s_margin", "url", "image",
]


def fmt(value, digits=1):
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return value


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CSV_FIELDS)
        for r in rows:
            out = []
            for k in CSV_FIELDS:
                v = r[k]
                if k == "similar_stores":
                    v = ";".join(v)
                elif k in ("price", "cost"):
                    v = fmt(v, 2)
                elif k == "margin":
                    v = fmt(v, 3)
                else:
                    v = fmt(v)
                out.append(v)
            w.writerow(out)


def write_html(rows, path, stores_summary, top, generated):
    e = html.escape
    cards = []
    for r in rows[:top]:
        img = (f'<img src="{e(r["image"])}" alt="" loading="lazy">' if r["image"]
               else '<div class="noimg">no image</div>')
        bars = "".join(
            f'<div class="bar" title="{label} {r[key]:.1f} / {weight}">'
            f'<span>{label}</span><i style="width:{100 * r[key] / weight:.0f}%"></i></div>'
            for key, label, weight in (
                ("s_bestseller", "Best-seller", W_BESTSELLER), ("s_similar", "Similar", W_SIMILAR),
                ("s_price", "Price", W_PRICE), ("s_recent", "Recent", W_RECENT), ("s_margin", "Margin", W_MARGIN),
            )
        )
        meta = [f'${r["price"]:.2f}' if r["price"] is not None else "no price"]
        if r["bestseller_rank"]:
            meta.append(f'best-seller #{r["bestseller_rank"]}')
        if r["margin"] is not None:
            meta.append(f'margin {r["margin"] * 100:.0f}%')
        if r["published_at"]:
            meta.append(f'published {r["published_at"]}')
        if not r["available"]:
            meta.append("sold out")
        similar = (f'<p class="sim">Similar at: {e(", ".join(r["similar_stores"]))}</p>'
                   if r["similar_stores"] else "")
        cards.append(f"""
<article>
  <a href="{e(r["url"])}" target="_blank" rel="noopener">{img}</a>
  <div class="body">
    <div class="top"><span class="rank">#{r["rank"]}</span><span class="score">{r["score"]:.0f}</span></div>
    <h2><a href="{e(r["url"])}" target="_blank" rel="noopener">{e(r["title"])}</a></h2>
    <p class="store">{e(r["store"])}{" · " + e(r["product_type"]) if r["product_type"] else ""}</p>
    <p class="meta">{e(" · ".join(meta))}</p>
    {similar}
    <div class="bars">{bars}</div>
  </div>
</article>""")

    summary = "".join(f"<li><b>{e(name)}</b>: {e(msg)}</li>" for name, msg in stores_summary)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Product Research Report</title>
<style>
:root {{ --bg:#f6f6f4; --card:#fff; --text:#1d1d1b; --muted:#6b6b66; --line:#e3e3de; --accent:#2f6f4f; --track:#ecece7; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#161615; --card:#21211f; --text:#ececea; --muted:#a2a29c; --line:#34342f; --accent:#6cc497; --track:#2e2e2a; }}
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:14px/1.45 system-ui, -apple-system, Segoe UI, sans-serif; }}
header {{ padding:24px 16px 8px; max-width:1200px; margin:0 auto; }}
h1 {{ margin:0 0 4px; font-size:22px; }}
header p, header li {{ color:var(--muted); }}
header ul {{ margin:8px 0; padding-left:18px; }}
main {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(240px, 1fr)); gap:16px; padding:16px; max-width:1200px; margin:0 auto; }}
article {{ background:var(--card); border:1px solid var(--line); border-radius:10px; overflow:hidden; display:flex; flex-direction:column; }}
article img, .noimg {{ width:100%; aspect-ratio:1; object-fit:cover; display:block; background:var(--track); }}
.noimg {{ display:flex; align-items:center; justify-content:center; color:var(--muted); }}
.body {{ padding:12px; }}
.top {{ display:flex; justify-content:space-between; align-items:baseline; }}
.rank {{ color:var(--muted); font-weight:600; }}
.score {{ font-size:22px; font-weight:700; color:var(--accent); }}
h2 {{ font-size:15px; margin:4px 0; }}
h2 a {{ color:inherit; text-decoration:none; }}
h2 a:hover {{ text-decoration:underline; }}
.store, .meta, .sim {{ margin:2px 0; color:var(--muted); font-size:12px; }}
.bars {{ margin-top:8px; display:grid; gap:3px; }}
.bar {{ position:relative; height:16px; background:var(--track); border-radius:3px; overflow:hidden; font-size:10px; }}
.bar i {{ position:absolute; inset:0 auto 0 0; background:var(--accent); opacity:.35; }}
.bar span {{ position:relative; padding-left:5px; line-height:16px; }}
</style>
</head>
<body>
<header>
  <h1>Product Research Report</h1>
  <p>Generated {e(generated)} · {len(rows)} products scored · top {min(top, len(rows))} shown.
  Score = best-seller rank (35) + similar at other stores (20) + ${PRICE_LOW:.0f}–{PRICE_HIGH:.0f} price (20) + recency (15) + margin (10).</p>
  <ul>{summary}</ul>
</header>
<main>{"".join(cards)}
</main>
</body>
</html>
"""
    Path(path).write_text(page, encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stores", default="stores.txt", help="file with one store domain per line")
    ap.add_argument("--costs", default="costs.csv", help="optional CSV with handle,cost[,store]")
    ap.add_argument("--out-dir", default="output", help="where to write the CSV and HTML report")
    ap.add_argument("--max-pages", type=int, default=10, help="max /products.json pages per store")
    ap.add_argument("--bestseller-pages", type=int, default=5, help="max best-seller collection pages per store")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    ap.add_argument("--top", type=int, default=200, help="products shown in the HTML report")
    args = ap.parse_args(argv)

    stores = read_stores(args.stores)
    if not stores:
        log(f"No stores in {args.stores}")
        return 1
    costs = read_costs(args.costs)
    if costs:
        log(f"Loaded {len(costs)} costs from {args.costs}")

    fetcher = Fetcher(delay=args.delay)
    store_data, summary = {}, []
    for base in stores:
        name = store_name(base)
        log(f"{name}")
        try:
            products = fetch_products(fetcher, base, args.max_pages)
        except Exception as e:  # keep going with the other stores
            log(f"  failed to fetch products: {e}")
            summary.append((name, f"failed: {e}"))
            continue
        try:
            handles = {(p.get("handle") or "").lower() for p in products}
            bestsellers = fetch_bestseller_order(fetcher, base, handles, args.bestseller_pages)
        except Exception as e:
            log(f"  failed to fetch best-sellers: {e}")
            bestsellers = []
        store_data[base] = (products, bestsellers)
        summary.append((name, f"{len(products)} products, {len(bestsellers)} in best-seller order"))

    if not store_data:
        log("No store returned products; nothing to score.")
        return 1

    now = datetime.now(timezone.utc)
    rows = build_rows(store_data, costs, now)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    write_csv(rows, out / "products_ranked.csv")
    write_html(rows, out / "report.html", summary, args.top, now.strftime("%Y-%m-%d %H:%M UTC"))
    log(f"Wrote {out / 'products_ranked.csv'} and {out / 'report.html'} ({len(rows)} products)")

    print(f"\nTop {min(10, len(rows))}:")
    print(f"{'#':>3} {'score':>5}  {'price':>8}  {'store':<22} title")
    for r in rows[:10]:
        price = f"${r['price']:.2f}" if r["price"] is not None else "-"
        print(f"{r['rank']:>3} {r['score']:>5.1f}  {price:>8}  {r['store']:<22} {r['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
