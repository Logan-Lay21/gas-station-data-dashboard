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

st.title('Top 5 Products by Weekly Sales')
st.write('A look at the top 5 products by average weekly sales for a given store, and sales fluctuating over time.')

items = scan_items()
gtin = load_master_gtin()


#%%
# input for store ID
#===============================================
input_store = st.text_input('Enter your store ID (If testing, use 25255)')
#===============================================

# TABLE FOR QUESTION 1
#===========================
tab1, tab2 = st.tabs(["All Time", "Manual Date Entry"])

with tab2:
    st.subheader("Select Date Range for Temporal Analysis")
    start, end = st.columns(2)
    # input for start date 
    #===============================================
    with start:
        start_date = st.date_input("Start Date (If testing, use 2023/01/01)", dt.date(dt.datetime.now().year, 1, 1))
    #===============================================

    # input for end date
    #===============================================
    with end:
        end_date = st.date_input("End Date (If testing, use 2023/06/01)", dt.date(dt.datetime.now().year, dt.datetime.now().month, dt.datetime.now().day))
    #===============================================


# input_store = '25255'

# create table
q1 = items\
    .filter(pl.col('STORE_ID') == input_store)\
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
    .sort('AVG_WEEKLY_SALES', descending=True)\
    .collect()\
    .join(gtin, on='GTIN', how='left')\
    .select(
        'GTIN',
        'AVG_WEEKLY_SALES',
        'AVG_WEEKLY_SOLD'
    )\
    .head(5)
        # 'CATEGORY',
        # 'SKUPOS_DESCRIPTION',



#===============================


#%%


q1_temporal = items\
    .filter(pl.col('STORE_ID') == input_store)\
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
    pl.max('TOTAL_SALES').alias('MAX_WEEKLY_SALES')
    )\
    .sort('MAX_WEEKLY_SALES', descending=True)


#%%

metric = items.collect()\
    .filter(pl.col('STORE_ID') == input_store)\
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
    pl.max('TOTAL_SALES').alias('MAX_WEEKLY_SALES')
    )\
    .sort('MAX_WEEKLY_SALES', descending=True)



#%%


# START COL 1 =============================================
# DISPLAY METRIC (RECORD WEEKLY SALES)
#================================
# top_row = (
#     metric
#     .sort("MAX_WEEKLY_SALES", descending=True)
#     .head(1)
#     .row(0, named=True)
# )

# with col1:
#     st.metric(
#     label="🏆 Top Product (Record Weekly Sales)",
#     value=f"GTIN {top_row['GTIN']}",
#     delta=f"${top_row['MAX_WEEKLY_SALES']:,.2f}"
# )



#===============================

#%%
q1 = q1\
    .rename(
        {
            'GTIN': 'GTIN',
            'AVG_WEEKLY_SALES': 'Avg Weekly Sales',
            'AVG_WEEKLY_SOLD': 'Avg Weekly Sold'
        }
    )
#%%

pdf = q1.to_pandas()  # your dataframe name here

fig = px.scatter(
    pdf,
    x="Avg Weekly Sold",
    y="Avg Weekly Sales",
    text="GTIN",
    title="Top 5 Items: Sales vs Units Sold",
)

fig.update_traces(
    textposition="top center",
    marker=dict(size=12)
)

fig.update_layout(
    title_x=0.5
)

with tab1:
    st.subheader("Top 5 Selling Items by Average Weekly Sales")
    # DISPLAY QUESTION 1 TABLE IN STREAMLIT
    #================================
    table, graph = st.columns([1, 2])  # Adjust the ratio as needed
    with table:
        st.write('Top 5 Products by Average Weekly Sales')
        st.dataframe(q1)
    
    with graph:
        st.plotly_chart(fig, use_container_width=True)
    #================================

# END COL 1 ===============================================
#%%
temporal_table = q1_temporal\
    .collect()\
    .head(5)\
    .rename({'GTIN': 'GTIN', 'MAX_WEEKLY_SALES': 'Top Weekly Sales'})

#%%
# START COL 2 =============================================


# st.subheader("Top Weekly Sales by GTIN")

pdf2 = temporal_table.to_pandas()

pdf2["GTIN"] = pdf2["GTIN"].astype(str)

pdf2 = pdf2.sort_values("Top Weekly Sales", ascending=False)

fig2 = px.bar(
    pdf2,
    x="GTIN",
    y="Top Weekly Sales",
    title="Top Weekly Sales by GTIN"
)

fig2.update_layout(
    title_x=0.5,
    xaxis_tickangle=-45,
    xaxis_title="GTIN (Product ID)",
    yaxis_title="Top Weekly Sales $",
    xaxis=dict(type="category")
    )


with tab2:
    table2, graph2 = st.columns([1, 2])  # Adjust the ratio as needed
    with table2:
        st.write('Top 5 Weekly Sales Within Selected Dates')
        st.dataframe(temporal_table)
    with graph2:
        st.plotly_chart(fig2, use_container_width=True)

# END COL 2 ===============================================


# %%
