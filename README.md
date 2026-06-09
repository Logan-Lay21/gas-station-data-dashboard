# Gas Station Data Dashboard

An interactive Streamlit dashboard built for gas station owners to explore store-level sales performance and customer behavior. Built on real transactional data from gas stations across Idaho and Utah.

**[Live Demo](https://app-challenge-wi26-hathaway-git-292414558216.us-west3.run.app/)**

---

## Overview

This dashboard was built as a class project using real transactional data provided by gas station operators. It is designed for store owners to monitor product performance, identify underperforming items, and understand how customers pay.

## Pages

- **Home** — Overview and navigation guide
- **Top Five Products** — Highest-performing products by weekly sales
- **Poor Selling Beverages** — Underperforming beverage brands by sales and demand metrics
- **Cash vs Credit** — Purchasing behavior comparison across payment types

## Tools Used

| Tool | Purpose |
|---|---|
| Python | Core language |
| Streamlit | Dashboard framework |
| Polars | Data wrangling |
| Plotly / Altair | Visualization |
| Docker | Containerization |
| Google Cloud Run | Deployment |

## Data not on the repo

Data is not included in this repo as it is proprietary. The dashboard is viewable via the live demo link above.


## Running Locally

Requirements: Docker

```bash
git clone https://github.com/Logan-Lay21/gas-station-dashboard
cd gas-station-dashboard
docker compose up --build
```

Then open `http://localhost:8080` in your browser.
