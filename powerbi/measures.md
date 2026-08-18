# Power BI Model and DAX Measures

In case Power BI is not available, this file documents the model and all measures in the report.

## Model

Four tables in a star schema, loaded from the CSVs in `data/`:

| Table | Source | Notes |
|---|---|---|
| `Fact_Orders` | `orders_clean.csv` | kept only 10 columns through Power Query, see below |
| `Dim_Products` | `products.csv` | SKU, Product Name, Category, Color, Cost of Goods |
| `Dim_Channels` | `channels.csv` | Channel, Avg Fee Pct, Avg Shipping Cost |
| `Dim_Date` | built in DAX | see below |

All the relationships are one-to-many, dimension to fact, single direction. `Dim_Products[SKU]`, `Dim_Channels[Channel]` and `Dim_Date[Date]` each join to the matching column in `Fact_Orders`.

**Excluded from import:** `orders_clean.csv` also contains `product_name`, `category`, `cost_of_goods`, `revenue`, `net_revenue`, `cost` and `gross_margin_pct` from the Python analysis. I left out the first three because they belong to the products table and I can already get them through the SKU relationship. The other four I wanted as measures instead of stored columns.

### Dim_Date

```dax
Dim_Date =
ADDCOLUMNS(
    CALENDARAUTO(),
    "Year", YEAR([Date]),
    "Month Number", MONTH([Date]),
    "Month Name", FORMAT([Date], "MMMM"),
    "Quarter", "Q" & FORMAT([Date], "Q"),
    "Year Month", FORMAT([Date], "MMM YYYY")
)
```

```dax
Year Month Number = Dim_Date[Year] * 100 + Dim_Date[Month Number]
```

Marked as the official date table. Two sort-by columns are needed so months sort chronologically rather than alphabetically.

### Naming

Tables use `Title_Case_With_Underscores`, columns use plain `Title Case` with spaces. Measures are located in a dedicated `_Measures` table.

## Measures

### Revenue and cost

```dax
Total Revenue = SUMX(Fact_Orders, Fact_Orders[Unit Price] * Fact_Orders[Units Sold])
```

```dax
Total Cost = SUMX(Fact_Orders, RELATED(Dim_Products[Cost of Goods]) * Fact_Orders[Units Sold])
```

```dax
Net Revenue = [Total Revenue] - SUM(Fact_Orders[Discount Amount]) - SUM(Fact_Orders[Platform Fee])
```

Shipping is billed separately from the sale and the referral fee does not apply to it so it does not affect revenue.

### Margin and rates

```dax
Gross Margin % = DIVIDE(
    [Total Revenue] - [Total Cost] - SUM(Fact_Orders[Platform Fee]),
    [Total Revenue]
)
```

This takes out the platform fee but not the discount, same as query 4 and the notebook. Query 2 leaves the fee out on purpose so I can compare categories without the channel mix affecting it.

```dax
Return Rate % = DIVIDE(
    COUNTROWS(FILTER(Fact_Orders, Fact_Orders[Return Flag] = TRUE())),
    COUNTROWS(Fact_Orders)
)
```

```dax
MoM Revenue Growth % =
VAR CurrentRevenue = [Total Revenue]
VAR PreviousMonthRevenue =
    CALCULATE(
        [Total Revenue],
        DATEADD(Dim_Date[Date], -1, MONTH)
    )
RETURN
    DIVIDE(CurrentRevenue - PreviousMonthRevenue, PreviousMonthRevenue)
```

### Channel price comparison

These four answer the same question as query 11: What would Amazon FBM have to charge to earn the same margin the website earns on the same SKU?

```dax
Website Price = CALCULATE(MAX(Fact_Orders[Unit Price]), Dim_Channels[Channel] = "Website")
```

```dax
FBM Price = CALCULATE(MAX(Fact_Orders[Unit Price]), Dim_Channels[Channel] = "Amazon FBM")
```

```dax
Required FBM Price =
VAR ItemCost = MAX(Dim_Products[Cost of Goods])
VAR WebPrice = [Website Price]
VAR FbmPrice = [FBM Price]
VAR Fee = CALCULATE(MAX(Dim_Channels[Avg Fee Pct]), Dim_Channels[Channel] = "Amazon FBM")
VAR WebMargin = DIVIDE(WebPrice - ItemCost, WebPrice)
RETURN
    IF(
        ISBLANK(WebPrice) || ISBLANK(FbmPrice),
        BLANK(),
        DIVIDE(ItemCost, (1 - Fee) - WebMargin)
    )
```

Website margin is `(price - cost) / price` since there is no platform fee there. FBM margin at price F is `((1 - fee) * F - cost) / F`. If I set those equal and solve for F I get `cost / ((1 - fee) - website_margin)`.

Nine of the 170 SKUs sold on only one channel or never sold. Without the guard they return a number instead of blank.

```dax
FBM Uplift Needed % = DIVIDE([Required FBM Price], [FBM Price]) - 1
```

These measures are only correct at SKU grain. Basic and fashion colors in the same style have different costs, so at Product Name grain `MAX(Cost of Goods)` picks one color's cost and prices the rest of the style against it.

### Report helper

```dax
Selected Category = SELECTEDVALUE(Dim_Products[Category], "All Categories")
```

Used for the card to display the drill-through selection. If nothing is selected, it defaults to "All Categories."

## Report pages

| Page | Contents |
|---|---|
| Executive Summary | four KPI cards, monthly revenue trend, revenue by category |
| Channel Comparison | same-SKU margin by channel, the required-FBM-price table, category and year slicers |
| Product Deep Dive | revenue by style with drill-down into color, channel affinity matrix; also the drill-through target for category |
| Category Tooltip | hidden page, surfaces margin and return rate on hover over the Executive Summary category chart |
