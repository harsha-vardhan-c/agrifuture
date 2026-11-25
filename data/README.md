# Data dictionary and provenance

## Price source

The price snapshot was assembled from **AGMARKNET** official Government of India report responses for Karnataka commodity/district monthly wholesale prices. Full original captured API report responses, including extraction metadata where present, are preserved in `raw/agmarknet_official_api_reports.json.gz` (compressed JSON). `raw/price_source_report_dates.csv` records source-date coverage. Report data was grouped consistently into district-month values after filtering to Karnataka, normalizing crop/district spellings, parsing dates and price numbers, and removing invalid, missing, duplicate or non-positive observations.

Run `python -m scripts.audit_source` to verify **each of the 13,552 final rows** against the matching district entry in the captured report specified by `raw/price_source_report_dates.csv`. The source audit passes on the ZIP's original snapshot. This audit script reads without rewriting the records.

**This is not synthetic training data.** Rows in `karnataka_prices.csv` are derived from real reports; price snapshots should still be re-audited against the publishing authority before operational decisions. The source can revise historic observations. The project uses the captured reports for reproducible offline operation, not a guaranteed real-time connection to AGMARKNET.

Source portal: https://agmarknet.gov.in/

## Main table: `karnataka_prices.csv`

| Field | Type | Meaning |
|---|---|---|
| `date` | `YYYY-MM-01` | Month start of the reported wholesale-price period |
| `crop` | text | Normalized vegetable commodity name |
| `district` | text | Normalized Karnataka reporting district name |
| `wholesale_price_rs_per_quintal` | positive float | Monthly district wholesale price, **Indian rupees / 100 kg** |

One row corresponds to one **crop + district + month**. The file has 13,552 unique rows, October 2021 through September 2026. It is **not** a list of individually reported invoices, transactions or retail prices. A value reported for Bengaluru should not be presented as the price at a particular physical mandi.

## Supporting files

| Path | What it means |
|---|---|
| `crop_coverage.csv` | Per-commodity source identifier and record/coverage counts |
| `crop_district_coverage.csv` | Data availability across specific crop–district combinations |
| `five_year_seasonal_average.csv` | Historical month-of-year price summaries for descriptive exploration |
| `horizon_training_features.csv` | Reproducible supervised examples; each target appears **after** its origin |
| `karnataka_weather_8_cities_2021_2026.csv` | Historical city-coordinate temperature/rainfall from Open-Meteo climate reanalysis |
| `raw/price_source_report_dates.csv` | Report source coverage and extraction-date records |
| `raw/agmarknet_official_api_reports.json.gz` | Unmodified compressed source-report response archive |

## Coverage gaps

- **Generic Pumpkin and Spinach:** planned commodities without usable source records; no dummy examples inserted.
- **Okra:** usable older observations, but no recent consecutive month sequence at the September 2026 forecast origin; it cannot be forecast with the current model inputs.
- Some other crop–district pairs have gaps. The API lists only combinations with eligible training history and the last three consecutive price months; it never silently uses a different district.
- There are **20 crops with at least one recorded price** and **371 crop/district time series** overall. Not every series is model-eligible.

## Weather provenance

The file `karnataka_weather_8_cities_2021_2026.csv` contains 480 city-month records for eight Karnataka city coordinates from the Open-Meteo historical archive/reanalysis. This is historical *city-proxy* information, not observations from every Karnataka farm or a true 12-month forecast. The live API is https://open-meteo.com/en/docs and is used only when the user opens results for a supported city. Both kinds of weather context are **excluded from the price regression features**; no claim of causality is made.

## Refreshing responsibly

1. Retrieve updated official AGMARKNET report data with the same crop and district definitions.
2. Preserve original API responses and retrieval provenance.
3. Re-run normalization and deduplication; inspect missing months and extreme prices.
4. Replace the main CSV only after confirming its schema, real dates and non-duplicate series.
5. Retrain (`python -m backend.train`) and re-run tests. Expand the backtest origins when new years become available.

This ZIP ships the **verified snapshot**, rather than a data-collection script that might depend on undocumented changing government endpoints or credentials.
