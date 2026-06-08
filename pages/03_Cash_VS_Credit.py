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

st.title('Cash vs Credit Customers')
st.write('A comparison of the top products, total sales, and total items purchased between cash and credit customers for a given store and date range.')

items = scan_items()
payments = load_payments()


#%%


#QUESTION 3 TABLE CREATION
#==================================
# input for store ID
#===============================================
input_store3 = st.text_input('Enter your store ID (If testing, use 25255)')
#===============================================

#Input to define the specific store
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



# input_store3 = '25255'

# CREATE TABLE FOR CASH CUSTOMERS
q3Cash = items.collect()\
    .filter(pl.col('STORE_ID') == input_store3)\
    .filter(
    (pl.col("DATE_TIME") >= start_date) &
    (pl.col("DATE_TIME") <= end_date)
    )\
    .with_columns(
    pl.when(pl.col("NONSCAN_CATEGORY") == "FUEL")
      .then(pl.lit("fuel"))
      .otherwise(pl.col("GTIN"))
      .alias("GTIN2")
    )\
    .join(payments, on=['STORE_ID', 'TRANSACTION_SET_ID'], how='left')\
    .select(
        'TRANSACTION_ITEM_ID',
        'PAYMENT_TYPE',
        'GTIN2',
        'UNIT_QUANTITY',
        'GRAND_TOTAL_AMOUNT'
    )\
    .filter(pl.col('PAYMENT_TYPE').is_in(['CASH']))\
    .group_by(
        'PAYMENT_TYPE',
        'GTIN2'
    )\
    .agg(
        pl.count('TRANSACTION_ITEM_ID').alias('TOTAL_TRANSACTIONS'),
        pl.sum('UNIT_QUANTITY').alias('TOTAL_UNITS'),
        pl.sum('GRAND_TOTAL_AMOUNT').alias('TOTAL_SALES')
    )\
    .sort('TOTAL_SALES', descending=True)\
    .head(5)


# CREATE TABLE FOR CREDIT CUSTOMERS
q3Credit = items.collect()\
    .filter(pl.col('STORE_ID') == input_store3)\
    .filter(
    (pl.col("DATE_TIME") >= start_date) &
    (pl.col("DATE_TIME") <= end_date)
    )\
    .with_columns(
    pl.when(pl.col("NONSCAN_CATEGORY") == "FUEL")
      .then(pl.lit("fuel"))
      .otherwise(pl.col("GTIN"))
      .alias("GTIN2")
    )\
    .join(payments, on=['STORE_ID', 'TRANSACTION_SET_ID'], how='left')\
    .select(
        'TRANSACTION_ITEM_ID',
        'PAYMENT_TYPE',
        'GTIN2',
        'UNIT_QUANTITY',
        'GRAND_TOTAL_AMOUNT'
    )\
    .filter(pl.col('PAYMENT_TYPE').is_in(['CREDIT']))\
    .group_by(
        'PAYMENT_TYPE',
        'GTIN2'
    )\
    .agg(
        pl.count('TRANSACTION_ITEM_ID').alias('TOTAL_TRANSACTIONS'),
        pl.sum('UNIT_QUANTITY').alias('TOTAL_UNITS'),
        pl.sum('GRAND_TOTAL_AMOUNT').alias('TOTAL_SALES')
    )\
    .sort('TOTAL_SALES', descending=True)\
    .head(5)
#===============================


# DISPLAY QUESTION 3 PART 1 IN STREAMLIT
#===============================
q3 = q3Cash.vstack(q3Credit) # Bring the two tables together
q3pt1 = q3
# st.dataframe(q3pt1)
#===============================


#%%


#Create table for question 3 part 2
#===============================
q3pt2 = q3\
    .group_by('PAYMENT_TYPE')\
    .agg(
        pl.sum('TOTAL_SALES').round(2).alias('TOTAL_SALES')
    )


pdf = q3pt2.to_pandas()  # easiest bridge to plotly

fig = px.pie(
    pdf,
    names="PAYMENT_TYPE",
    values="TOTAL_SALES",
    title="Total Sales by Payment Type",
    hole=0.3  # makes it a donut chart (instantly more professional-looking 😎)
)

fig.update_traces(
    textinfo="label+value",
    pull=[0.05, 0]
)
#===============================


# %%


# DISPLAY QUESTION 3 PART 2 IN STREAMLIT
#===============================
# st.dataframe(q3pt2)
#===============================


# %%


# Create table for question 3 part 3
#===============================
q3pt3 = q3\
    .group_by('PAYMENT_TYPE')\
    .agg(
        pl.sum('TOTAL_UNITS').round(2).alias('TOTAL_UNITS')
    )

pdf2 = q3pt3.to_pandas()  # easiest bridge to plotly

fig2 = px.pie(
    pdf2,
    names="PAYMENT_TYPE",
    values="TOTAL_UNITS",
    title="Total Units by Payment Type",
    hole=0.3
)

fig2.update_traces(
    textinfo="label+value",  # 👈 no percentages, just label + raw value
    pull=[0.05, 0]  # 👈 pull the first slice out a bit for emphasis
)

fig2.update_layout(title_x=0.5)



#===============================

#%%


# DISPLAY QUESTION 3 PART 3 IN STREAMLIT
#===============================
# st.dataframe(q3pt3)
#===============================


# %%


# CREATE TABS FOR 3 VIEWS

tab1, tab2, tab3 = st.tabs(["Products", "Purchases", "# of Items"])

with tab1:
    st.header("Cash vs Credit: Top Products")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cash Customers")
        st.dataframe(q3Cash)
    with col2:
        st.subheader("Credit Customers")
        st.dataframe(q3Credit)

with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Cash vs Credit: Total Purchases")
        st.dataframe(q3pt2)
    with col2:
        st.plotly_chart(fig, use_container_width=True)
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cash vs Credit: Total Items Purchased")
        st.dataframe(q3pt3)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

#%%