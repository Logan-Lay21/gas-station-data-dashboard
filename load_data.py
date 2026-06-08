# load_data.py
import polars as pl
import streamlit as st
from pathlib import Path

# Base folder relative to this file
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# ------------------------
# CACHED LOADERS
# ------------------------
@st.cache_data
def load_master_gtin():
    return pl.read_parquet(DATA_DIR / "cstore_master_ctin.parquet")

@st.cache_data
def load_discounts():
    return pl.read_parquet(DATA_DIR / "cstore_discounts.parquet")

@st.cache_data
def load_stores():
    return pl.read_parquet(DATA_DIR / "cstore_stores.parquet")

@st.cache_data
def load_payments():
    return pl.read_parquet(DATA_DIR / "cstore_payments.parquet")

@st.cache_data
def load_daily():
    return pl.read_parquet(DATA_DIR / "cstore_transactions_daily_agg.parquet")

@st.cache_data
def load_shopper():
    return pl.read_parquet(DATA_DIR / "cstore_shopper.parquet")

@st.cache_data
def load_sets():
    return pl.read_parquet(DATA_DIR / "cstore_transaction_sets.parquet")

@st.cache_data
def load_status():
    return pl.read_parquet(DATA_DIR / "cstore_store_status.parquet")

@st.cache_data
def scan_items():
    return pl.scan_parquet(DATA_DIR / "transaction_items")
# %%
