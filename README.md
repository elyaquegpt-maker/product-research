# Product Research

`research.py` ranks products from a list of Shopify stores. It uses only the Python 3 standard library: no installs needed.

## Usage

```sh
python3 research.py
```

1. Reads `stores.txt`: one store domain per line (`kith.com`, or a full `https://...` URL). Blank lines and `#` comments are ignored.
2. For each store, downloads `/products.json?limit=250&page=N`, up to 10 pages (2,500 products).
3. Gets best-seller order by scraping product links from `/collections/all?sort_by=best-selling` (up to 5 pages).
4. Scores every product from 0 to 100 and writes:
   - `output/products_ranked.csv`: all products, ranked, with a breakdown of each score component
   - `output/report.html`: image cards for the top 200 products, opened in any browser

It waits 1 second between requests and retries on HTTP 429/5xx (it honors `Retry-After`). A store that fails is skipped and listed in the report header.

Options: `--stores`, `--costs`, `--out-dir`, `--max-pages`, `--bestseller-pages`, `--delay`, `--top`. Run `python3 research.py -h` for details.

## Scoring (0–100)

| Component | Max | How |
|---|---|---|
| Best-seller rank | 35 | #1 in the store's best-seller order gets 35, falling linearly through the list. Products not in the list get 0. |
| Similar product at other stores | 20 | Counts *other* stores selling a product whose title tokens have Jaccard similarity ≥ 0.4 with this one. 3+ stores gives full points. |
| Price sweet spot | 20 | Lowest variant price between $25 and $90 gets 20. Below $25, points scale down linearly toward $0. Above $90, they reach 0 at $180. |
| Recently published | 15 | Published within 30 days gets 15, falling to 0 at 365 days. |
| Margin | 10 | `(price − cost) / price`. A 70%+ margin gets 10. Needs `costs.csv`. |

Without `costs.csv`, no product gets margin points, so the maximum score is 90.

The constants at the top of `research.py` set the weights and thresholds.

## costs.csv (optional)

```csv
handle,cost,store
wool-runner,22.50,www.allbirds.com
classic-tee,8
```

`handle` is the product's URL handle (`/products/<handle>`). `store` is optional: a row without it applies to that handle at any store. `costs.csv` is git-ignored.

## Caveats

- Some stores block or throttle `/products.json` or render best-seller grids with JavaScript. Those stores get fewer (or no) best-seller points.
- "Similar" compares titles only, so it's a rough signal.
