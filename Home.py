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
st.markdown("""
# Gas Station Data Dashboard

Welcome! This dashboard explores product performance and customer behavior through interactive visualizations built from real transactional data.

---

### What You Can Explore

**Top Five Products**  
Identify the highest-performing products based on weekly sales and surface what's driving revenue.

**Poor Selling Beverages**  
Analyze underperforming beverage brands using sales and demand metrics to identify products that may need to be reconsidered or removed.

**Cash vs Credit**  
Compare purchasing behavior across payment types — see how customers using cash vs credit differ in spending habits and product choices.

---

### ⚙️ How to Use

- Navigate through the pages on the left to explore each section
- Adjust filters (such as date ranges) where available
- Hover over charts for additional details

---

### Purpose

This dashboard transforms raw transactional data into clear, actionable insights — supporting better decisions around product performance, inventory, and customer behavior.
""")

# %%