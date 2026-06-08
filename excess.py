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
#%%

"""
# Welcome to Logan's Data Web App!
"""

gtin = pl.read_parquet('data/cstore_master_ctin.parquet')
discounts = pl.read_parquet('data/cstore_discounts.parquet')
stores = pl.read_parquet('data/cstore_stores.parquet')
payments = pl.read_parquet('data/cstore_payments.parquet')
daily = pl.read_parquet('data/cstore_transactions_daily_agg.parquet')
shopper = pl.read_parquet('data/cstore_shopper.parquet')
sets = pl.read_parquet('data/cstore_transaction_sets.parquet')
status = pl.read_parquet('data/cstore_store_status.parquet')
items = pl.scan_parquet('data/transaction_items')


#%%

# TABLE FOR QUESTION 1
#===========================

# input for store ID
input_store = st.text_input('Enter a store ID to see the top 5 selling items by average weekly sales')

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
        'CATEGORY',
        'SKUPOS_DESCRIPTION',
        'AVG_WEEKLY_SALES',
        'AVG_WEEKLY_SOLD'
    )\
    .head(5)

#===============================


#%%


# DISPLAY QUESTION 1 IN STREAMLIT
#================================
st.dataframe(q1)
#================================


# %%

input_store2 = st.text_input('Enter a store ID to see the top 10 beverage brands by average weekly sales recommended to drop')

# TABLE FOR QUESTION 2
#============================

q2 = items\
    .filter(pl.col('STORE_ID') == input_store2)\
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

# DISPLAY QUESTION 2 IN STREAMLIT
#===============================
st.dataframe(q2)
#===============================

#%%


#QUESTION 3 TABLE CREATION
#==================================

#Input to define the specific store
input_store3 = st.text_input('Enter a store ID to see how your cash and credit customers compare')
# input_store3 = '25255'

# CREATE TABLE FOR CASH CUSTOMERS
q3Cash = items.collect()\
    .filter(pl.col('STORE_ID') == input_store3) \
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
    .filter(pl.col('STORE_ID') == input_store3) \
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
st.dataframe(q3pt1)
#===============================


#%%


#Create table for question 3 part 2
#===============================
q3pt2 = q3\
    .group_by('PAYMENT_TYPE')\
    .agg(
        pl.sum('TOTAL_SALES').round(2).alias('TOTAL_SALES')
    )
#===============================


# %%


# DISPLAY QUESTION 3 PART 2 IN STREAMLIT
#===============================
st.dataframe(q3pt2)
#===============================


# %%


# Create table for question 3 part 3
#===============================
q3pt3 = q3\
    .group_by('PAYMENT_TYPE')\
    .agg(
        pl.sum('TOTAL_UNITS').round(2).alias('TOTAL_UNITS')
    )
#===============================

#%%


# DISPLAY QUESTION 3 PART 3 IN STREAMLIT
#===============================
st.dataframe(q3pt3)
#===============================


# %%


# CREATE TABLE FOR QUESTION 4

# stores.head(5)
# %%


location = stores\
    .filter(pl.col('STORE_ID').is_in([25255, 31631, 31632, 6385, 18191, 19075]))


# %%

tract_url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"

results = []

for row in location.iter_rows(named=True):
    store_id = row["STORE_ID"]
    lat = row["LATITUDE"]
    lon = row["LONGITUDE"]

    params = {
        "x": lon,
        "y": lat,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "layers": "Census Tracts",
        "format": "json"
    }

    r = requests.get(tract_url, params=params)
    data = r.json()

    # Step-by-step safe access
    if "result" in data and "geographies" in data["result"]:
        geos = data["result"]["geographies"]

        if "Census Tracts" in geos and len(geos["Census Tracts"]) > 0:
            tract_info = geos["Census Tracts"][0]

            results.append({
                "STORE_ID": store_id,
                "STATE_FIPS": tract_info["STATE"],
                "COUNTY_FIPS": tract_info["COUNTY"],
                "TRACT_FIPS": tract_info["TRACT"]
            })
        else:
            print(f"No tract found for store {store_id}")
            results.append({
                "STORE_ID": store_id,
                "STATE_FIPS": None,
                "COUNTY_FIPS": None,
                "TRACT_FIPS": None
            })
    else:
        print(f"Bad response for store {store_id}")
        results.append({
            "STORE_ID": store_id,
            "STATE_FIPS": None,
            "COUNTY_FIPS": None,
            "TRACT_FIPS": None
        })

tracts = pl.DataFrame(results)

locations = location.join(tracts, on="STORE_ID", how="left")


# %%


# PHASE 1: GET ACS DATA
#==============================

API = '2297d8f647cafebbcd631f1cbffc96beeb521a58'

acs_vars = [
    "B01001_001E",  # total population
    "B19301_001E",  # per capita income
    "B25064_001E",  # median rent
    "B23025_003E",  # labor force
    "B23025_005E",  # unemployed
    "B15003_017E",  # high school grads
    "B02001_002E",  # white alone
    "B25002_002E",  # owner occupied
    "B08203_001E",  # vehicles available
    "B25014_001E"   # rooms
]

acs_results = []

for row in locations.iter_rows(named=True):

    if None in (row["STATE_FIPS"], row["COUNTY_FIPS"], row["TRACT_FIPS"]):
        continue

    params = {
        "get": f"NAME,{','.join(acs_vars)}",
        "for": f"tract:{row['TRACT_FIPS']}",
        "in": f"state:{row['STATE_FIPS']}+county:{row['COUNTY_FIPS']}",
        "key": API
    }

    r = requests.get("https://api.census.gov/data/2023/acs/acs5", params=params)

    if r.status_code == 200:
        data = r.json()

        row_dict = dict(zip(data[0], data[1]))
        row_dict["STORE_ID"] = row["STORE_ID"]

        acs_results.append(row_dict)

acs_df = pl.DataFrame(acs_results)

#==============================


#%%

# PHASE 2: CLEAN AND CONVERT
#==============================

acs_df = acs_df.with_columns([
    pl.col(col).cast(pl.Float64)
    for col in acs_vars
])


acs_df = acs_df.rename({
    "B01001_001E": "population",
    "B19301_001E": "income_per_capita",
    "B25064_001E": "median_rent",
    "B23025_003E": "labor_force",
    "B23025_005E": "unemployed",
    "B15003_017E": "high_school_grads",
    "B02001_002E": "white_population",
    "B25002_002E": "owner_occupied",
    "B08203_001E": "vehicles",
    "B25014_001E": "rooms"
})
#==============================


# %%


# PHASE 3: JOIN TO STORES
#==============================
locations_demo = locations.join(acs_df, on="STORE_ID", how="left")

#==============================


#%%

avg_demo = locations_demo.select([
    pl.mean(col).alias(f"{col}_avg")
    for col in [
        "population",
        "income_per_capita",
        "median_rent",
        "labor_force",
        "unemployed",
        "high_school_grads",
        "white_population",
        "owner_occupied",
        "vehicles",
        "rooms"
    ]
])
# %%
comparison = locations_demo.join(avg_demo, how="cross")

for col in [
    "population",
    "income_per_capita",
    "median_rent",
    "labor_force",
    "unemployed",
    "high_school_grads",
    "white_population",
    "owner_occupied",
    "vehicles",
    "rooms"
]:
    comparison = comparison.with_columns(
        ((pl.col(col) - pl.col(f"{col}_avg")) / pl.col(f"{col}_avg") * 100)
        .alias(f"{col}_pct_diff")
    )
# %%
st.dataframe(comparison)
# %%
