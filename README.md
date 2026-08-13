# CrownCase Beauty — Channel Profitability Analysis

As part of my current role, I manage multi-channel selling: same catalog but multiple different storefronts. The main challenge with managing different storefronts with different fees is constantly determining margins and sales performance. 

Because I am unable to use data I work with and I am unable to find public data that is similar, I built a simulated retailer dataset that behaves like the one I know. CrownCase Beauty sells hair and wig products through its own website and through Amazon FBM (Fulfilled by Merchant). This project takes it end to end - Python for generation and analysis, SQL Server for storage and querying, Power BI for the report.

The questions below are some of the questions I answer in my current role and this project's aim is to demonstrate how I answer them with different tools.

## The Questions

- For the exact same SKU, how much does channel choice change profitability?
- Which categories bring in the most revenue and are those the same ones bringing the most margin?
- Is seasonality one blended curve across the catalog or does each category have its own?
- When we run a 10% discount, what does that actually cost us in margin?
- Do return rates differ by channel, category or individual style?
- Are there styles that do much better in one channel?

## About the Data

The dataset is roughly 10000 orders spanning January 2024 - December 2025, across four categories: Wigs, Lace Wigs, Weaves and Braids.

I tried to make the data generated similar to the data I have encountered in real life - fees, discounts, seasonality were based on what I have observed, though not exactly the same. 

I also introduced data quality problems (null values, inconsistent capitalization, wrong date formats, duplicate rows) to simulate the cleaning stage especially when I export data from third party channels.

Since I wrote the generator, the broad structure in the data is structure I put there, and I'm not presenting these results as evidence about the real wig market. What the project demonstrates is the full path from messy source data to a decision-ready report.

## Tools Used

- **Python** (pandas, numpy) — data generation, cleaning, exploratory analysis, visuals
- **SQL Server** (T-SQL) — storage, a raw-to-clean view layer, queries behind the business questions
- **Power BI Desktop** — 3-page report (Executive Summary, Channel Comparison, Product Deep Dive) on a star schema with DAX measures

## Report Preview

**Executive Summary**
![Executive Summary](images/executive-summary.png)

**Channel Comparison**
![Channel Comparison](images/channel-comparison.png)

**Product Deep Dive**
![Product Deep Dive](images/product-deep-dive.png)

If Power BI Desktop is not available, there's a PDF export at `powerbi/CrownCaseBeauty_Portfolio.pdf`. 

## How to Run It

1. Clone the repo.
2. Create and activate a virtual environment, then install dependencies:
   ```
   python -m venv venv
   venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```
3. Generate the data (run in order):
   ```
   python generate_products.py
   python generate_channels.py
   python generate_orders.py
   ```
   This produces `data/products.csv`, `data/channels.csv`, and `data/orders.csv` (the last one intentionally messy — see below).
4. Set up SQL Server (requires a local SQL Server instance):
   - Run `sql/01_create_schema.sql` to create the database and tables.
   - Stage the 3 CSVs somewhere the SQL Server service account can read (a folder directly under `C:\`, in my case I used `C:\SQLData`).
   - Run `sql/02_bulk_insert.sql` to load the CSVs.
   - Run `sql/03_cleaning_view.sql` to build the `orders_clean` view.
   - Run `sql/04_analytical_queries.sql` for the 10 business queries.
5. Run `notebooks/phase3_analysis.ipynb` — connects to SQL Server independently, re-cleans the raw `orders` table in pandas, engineers `net_revenue`/`gross_margin_pct`, produces 6 visualizations, and exports `data/orders_clean.csv` for Power BI.
6. Open `powerbi/CrownCaseBeauty_Portfolio.pbix` in Power BI Desktop — a 3-page report (Executive Summary, Channel Comparison, Product Deep Dive).

## Key Findings

Most of these aren't discoveries so much as confirmation that the pipeline correctly recovered what I already built into the generator. 

**Confirming the pipeline works:**

- Return rates sit around 8% across every channel, category and style. No real pattern anywhere. Expected, since return_flag was generated as a flat coin flip independent of all of those. This confirms the measurement is accurate, not that returns actually behave this way.
- Seasonality shows up as four separate curves, not one blended pattern. Wigs and lace wigs climb into November and December, weaves peak around February through April and braids run June through August. Both years hold the same shape. These curves were hand-designed into the generator.
- Units per order are flat across all four categories. Lace wigs' high AOV turns out to be pure price, not basket size. Units per order were generated independent of category, so this just confirms that independence held.
- The website out-margins Amazon FBM on every SKU sold through both channels, across 150+ SKUs, zero exceptions. Given how pricing was built (FBM's premium is small, its 15% fee isn't), this gap is close to guaranteed by construction.

**What actually emerged:**

- A 10% discount costs about 4.4 margin points, not 10. This is because discount amount is tied to unit price and units per order is a totally separate random variable. The 4.4 only shows up once the analysis is run.