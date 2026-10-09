# Product Research

Three scripts for finding products worth selling, plus `daily.py` to run them on a schedule. They use only the Python 3 standard library: no installs needed.

| Script | Answers |
|---|---|
| `research.py` | Which products look strongest across these stores right now? |
| `trends.py` | What changed since last time: climbers, new launches, price and stock moves? |
| `profit.py` | Can this product make money with paid ads? (break-even ROAS) |

It runs every day in the cloud on GitHub Actions (see [Runs in the cloud](#runs-in-the-cloud)). You can also run all three with `daily.py`, or one at a time:

```sh
python3 research.py      # output/products_ranked.csv, output/report.html, snapshots/YYYY-MM-DD.json
python3 trends.py        # output/trends.csv, output/trends.html
python3 profit.py        # output/profit.csv
```

## Runs in the cloud

`.github/workflows/daily-research.yml` runs `daily.py` on GitHub Actions every day at 06:17 UTC. Your computer doesn't need to be on.

Each run:
1. Restores past snapshots from the `data` branch.
2. Runs research → trends → profit. Snapshots older than 120 days are deleted (`KEEP_DAYS` in the workflow).
3. Saves the snapshots and latest reports to the `data` branch. That branch holds a single commit that is replaced on every run, so the repo doesn't grow forever.
4. Uploads `output/` and `logs/` as a downloadable artifact, kept for 30 days.

**Where to see results:**
- **Quick look:** repo → **Actions** → *Daily product research* → the latest run. The page shows the top 10, trends and profit summary (works on a phone).
- **Full reports:** download the `reports-N` artifact at the bottom of that run page, unzip it, and open `report.html` or `trends.html` in a browser.
- **History:** the `data` branch has `latest/` (CSVs, plus `README.md` with the summary) and `snapshots/`.

**Run it now:** Actions → *Daily product research* → **Run workflow**. The optional `cost_pct` input estimates missing costs as a percentage of price.

**Real supplier costs:** add the contents of your `costs.csv` as a repository secret named `COSTS_CSV` (Settings → Secrets and variables → Actions → New repository secret). The workflow only uses it when the **repository is private**. In a public repo, anyone can see the logs, run summary and artifacts, and the profit numbers would reveal your costs. A private repo gets 2,000 free Actions minutes a month, and a run takes a few minutes.

**Caveats:**
- GitHub can start scheduled runs late when it's busy.
- GitHub pauses schedules in public repos after 60 days without activity, and sends an email. Re-enable on the Actions tab.
- Shopify stores often block GitHub's servers outright: the first test run got HTTP 429 from all six seed stores. The run summary lists what each store returned.

**If stores block the runs:** send requests through a proxy. Most scraping proxy services (residential or rotating proxies) give you a URL like `http://user:pass@host:port`. Save it as a repository secret named `PROXY_URL`, and the workflow sends every request through it. With no secret set, requests go out directly.


```sh
python3 daily.py                  # research → trends → profit
python3 daily.py --days 7         # trends vs. a week ago instead of the last run
python3 daily.py --cost-pct 35    # profit with estimated costs where costs.csv has none
```

`daily.py` runs `research.py` first. It then runs `trends.py` once there are snapshots from two different days, and `profit.py` when `costs.csv` exists (or `--cost-pct` is given). It works from any folder and appends everything to `logs/YYYY-MM-DD.log`. It exits non-zero if a step fails. Reports are overwritten each day; the dated snapshots keep the history.

A run takes a few minutes, mostly because of the 1-second delay between requests. The computer needs to be on and online at the scheduled time.

**macOS / Linux (cron).** Run `crontab -e` and add a line, using your own paths (`which python3` shows the Python path). For 7:15 every morning:

```
15 7 * * * /usr/bin/python3 /path/to/product-research/daily.py >/dev/null 2>&1
```

On macOS, if the repo is in Documents, Desktop or Downloads, cron needs Full Disk Access: System Settings → Privacy & Security → Full Disk Access → add `/usr/sbin/cron`. Alternatively, keep the repo somewhere else, such as `~/product-research`.

**Windows (Task Scheduler).** In Command Prompt, using your own paths (`where python` shows the Python path):

```
schtasks /create /tn "Product Research" /sc daily /st 07:15 /tr "\"C:\Path\To\python.exe\" \"C:\path\to\product-research\daily.py\""
```

Run it once now with `schtasks /run /tn "Product Research"` and check `logs\`. Remove it with `schtasks /delete /tn "Product Research"`.

## research.py

1. Reads `stores.txt`: one store domain per line (`kith.com`, or a full `https://...` URL). Blank lines and `#` comments are ignored.
2. For each store, downloads `/products.json?limit=250&page=N`, up to 10 pages (2,500 products).
3. Gets best-seller order by scraping product links from `/collections/all?sort_by=best-selling` (up to 5 pages).
4. Scores every product from 0 to 100 and writes:
   - `output/products_ranked.csv`: all products, ranked, with a breakdown of each score component
   - `output/report.html`: image cards for the top 200 products, opened in any browser
   - `snapshots/YYYY-MM-DD.json`: today's catalog for `trends.py` (one per day, a rerun replaces it; `--no-snapshot` to skip)

It waits 1 second between requests and retries on HTTP 429/5xx (it honors `Retry-After`). A store that fails is skipped and listed in the report header.

Options: `--stores`, `--costs`, `--out-dir`, `--max-pages`, `--bestseller-pages`, `--delay`, `--top`, `--snapshot-dir`, `--no-snapshot`. Run `python3 research.py -h` for details.

### Scoring (0–100)

| Component | Max | How |
|---|---|---|
| Best-seller rank | 35 | #1 in the store's best-seller order gets 35, falling linearly through the list. Products not in the list get 0. |
| Similar product at other stores | 20 | Counts *other* stores selling a product whose title tokens have Jaccard similarity ≥ 0.4 with this one. 3+ stores gives full points. |
| Price sweet spot | 20 | Lowest variant price between $25 and $90 gets 20. Below $25, points scale down linearly toward $0. Above $90, they reach 0 at $180. |
| Recently published | 15 | Published within 30 days gets 15, falling to 0 at 365 days. |
| Margin | 10 | `(price − cost) / price`. A 70%+ margin gets 10. Needs `costs.csv`. |

Without `costs.csv`, no product gets margin points, so the maximum score is 90.

The constants at the top of `research.py` set the weights and thresholds.

## trends.py

Compares two snapshots. By default it uses the newest one and the one before it. `--days 7` compares against the newest snapshot at least 7 days older, and `--old`/`--new YYYY-MM-DD` pick exact dates.

Each changed product gets its strongest signal (plus any others in the `signals` column):

| Signal | Meaning |
|---|---|
| New in best-sellers | Was unranked (or didn't exist), now in the best-seller list |
| Climbing / Falling | Best-seller rank moved 5+ places |
| New launch | Not in the earlier snapshot |
| Price up / Price down | Price changed 5%+ |
| Back in stock / Sold out | Availability flipped |
| Left best-sellers | Was ranked, now unranked |
| Removed | No longer in the catalog |

Writes `output/trends.csv` (every change) and `output/trends.html` (grouped, with images). A store that failed to download in either snapshot is skipped, so a failed download doesn't show up as hundreds of "removed" products. `snapshots/` is git-ignored.

## profit.py

Reads `output/products_ranked.csv` and `costs.csv`, and works out the economics of each product **per order, before ad spend**:

```
profit          = price × (1 − return rate) − cost − shipping − payment fees
break-even ROAS = price / profit            # below this, ads lose money
max CPA         = profit                    # most you can spend in ads per order
target ROAS     = price / (profit − target margin × price)
```

Returned orders are treated as a full refund with the item written off (typical for dropshipping).

| Verdict | Break-even ROAS |
|---|---|
| great | ≤ 1.5 |
| good | ≤ 2.0 |
| risky | ≤ 3.0 |
| avoid | > 3.0, or loses money before ads |

Cold Meta traffic often lands around 1.5–3x ROAS, so a break-even below 2 leaves room to profit.

Assumptions (all flags): `--fee-pct 2.9 --fee-fixed 0.30` (Shopify Payments-style), `--return-rate 10`, `--target-margin 15`, `--shipping 0` (used when `costs.csv` has no shipping). Products without a cost are skipped unless you pass `--cost-pct 35`, which estimates cost as 35% of price and marks those rows `estimate`.

Writes `output/profit.csv`, sorted by verdict and then research score: the top rows sell well *and* leave room for ad spend.

## costs.csv (optional for research.py, needed for profit.py)

```csv
handle,cost,shipping,store
wool-runner,22.50,6,www.allbirds.com
classic-tee,8,,
```

`handle` is the product's URL handle (`/products/<handle>`). `shipping` and `store` are optional: a row without a store applies to that handle at any store. `research.py` uses only `cost`. `costs.csv` is git-ignored.

## Caveats

- Some stores block or throttle `/products.json` or render best-seller grids with JavaScript. Those stores get fewer (or no) best-seller points.
- "Similar" compares titles only, so it's a rough signal.
- `/products.json` returns at most 2,500 products per store here. For bigger catalogs, products outside that window can show up as "new" or "removed" in trends.
