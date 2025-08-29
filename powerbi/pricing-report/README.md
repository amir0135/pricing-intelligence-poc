# Power BI Pricing Report (PBIP)

This folder contains a PBIP-format Power BI project for the Pricing POC.

## How to Open
- Open this folder in Power BI Desktop (PBIP preview required).
- Dataflows load CSVs from `../../data/sample_csv`.

## Pages
- Overview: KPIs, margin trend, hit rate by segment
- Quote Simulator: parameters for quote, win curve chart, floor/target/stretch cards
- Performance: discount heatmap, time to quote, recommendation adoption

## Measures
- Margin = SUM(Orders[net_price] - RELATED(COGS[cogs]))
- Hit Rate = AVERAGE(Orders[won_flag])
- Avg Discount = AVERAGE(Orders[discount])

## Note
- In Quote Simulator, a Power Query function or Power Automate visual can call the API in future. For now, simulate with the curve table.
