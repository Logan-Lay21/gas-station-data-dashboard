#%%
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

#%%
from collections import namedtuple
import altair as alt
import plotly.express as px
import math
import polars as pl
import streamlit as st
from great_tables import GT, md, html
import requests
import numpy as np
import datetime as dt
from load_data import (
    load_master_gtin, load_discounts, load_stores, load_payments,
    load_daily, load_shopper, load_sets, load_status, scan_items
)
#%%

st.title('10 Worst Performing Beverage Brands')
st.write('A look at the 10 worst performing beverage brands by average weekly sales for a given store, and sales fluctuating over time.')

items = scan_items()
gtin = load_master_gtin()


# %%

# input for store ID
#===============================================
input_store2 = st.text_input('Enter your store ID (If testing, use 25255)')
#===============================================

col1, col2 = st.columns(2)


# input for start date 
#===============================================
with col1:
    start_date = st.date_input("Start Date (If testing, use 2023/01/01)", dt.date(dt.datetime.now().year, 1, 1))
#===============================================


# input for end date
#===============================================
with col2:
    end_date = st.date_input("End Date (If testing, use 2023/06/01)", dt.date(dt.datetime.now().year, dt.datetime.now().month, dt.datetime.now().day))
#===============================================


# TABLE FOR QUESTION 2
#============================

q2 = items\
    .filter(pl.col('STORE_ID') == input_store2)\
    .filter(
    (pl.col("DATE_TIME") >= start_date) &
    (pl.col("DATE_TIME") <= end_date)
    )\
    .with_columns(
        week = pl.col('DATE_TIME').dt.week().alias('week'),
        year = pl.col('DATE_TIME').dt.year().alias('year')
    )\
    .filter(pl.col('SCAN_TYPE') == 'GTIN')\
    .group_by(
        'week',
        'year',
        'GTIN'
    )\
    .agg(
        pl.sum('UNIT_QUANTITY').alias('TOTAL_UNITS'),
        pl.sum('GRAND_TOTAL_AMOUNT').alias('TOTAL_SALES')
    )\
    .group_by(
        'GTIN'
    )\
    .agg(
        pl.mean('TOTAL_SALES').round(2).alias('AVG_WEEKLY_SALES'),
        pl.mean('TOTAL_UNITS').round().alias('AVG_WEEKLY_SOLD'),
    )\
    .collect()\
    .join(gtin, on='GTIN', how='left')\
    .select(
        'GTIN',
        'CATEGORY',
        'BRAND',
        'AVG_WEEKLY_SALES',
        'AVG_WEEKLY_SOLD'
    )\
    .filter(pl.col('CATEGORY') == 'Packaged Beverages')\
    .group_by('BRAND')\
    .agg(
        pl.sum('AVG_WEEKLY_SALES').alias('AVG_WEEKLY_SALES'),
        pl.sum('AVG_WEEKLY_SOLD').alias('AVG_WEEKLY_SOLD')
    )\
    .sort('AVG_WEEKLY_SALES', descending=False)\
    .head(10)

#==============================


# %%

pdf = q2.to_pandas()

fig = px.scatter(
    pdf,
    x="AVG_WEEKLY_SOLD",
    y="AVG_WEEKLY_SALES",
    text="BRAND",
    title="Underperforming Beverage Brands (Weekly Performance)"
)

# labels on points
fig.update_traces(textposition="top center")

# center title
fig.update_layout(title_x=0.5)

# 🔥 quadrant lines (this is the magic)
fig.add_vline(
    x=pdf["AVG_WEEKLY_SOLD"].mean(),
    line_dash="dot"
)

fig.add_hline(
    y=pdf["AVG_WEEKLY_SALES"].mean(),
    line_dash="dot"
)


# DISPLAY QUESTION 2 IN STREAMLIT
#===============================

table, graph = st.columns([1,1])
with table:
    st.dataframe(q2)

with graph:
    st.plotly_chart(fig, use_container_width=True)

#===============================


# %%
# %%
