import streamlit as st
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect("sales_data.db")

# Load all data
@st.cache_data
def load_data():
    sales = pd.read_sql("SELECT * FROM Sales", conn)
    customers = pd.read_sql("SELECT * FROM Customers", conn)
    products = pd.read_sql("SELECT * FROM Products", conn)
    return sales, customers, products

sales, customers, products = load_data()

# -------- Sidebar Filters -------- #
st.sidebar.header("Filter Options")

# Location filter
locations = customers["Location"].dropna().unique()
selected_locations = st.sidebar.multiselect("Customer Location", locations, default=list(locations))

# Date filter (get from sales before filtering)
sales["Date"] = pd.to_datetime(sales["Date"])
min_date = sales["Date"].min()
max_date = sales["Date"].max()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

# -------- Filter Data -------- #

# Filter customers by location
filtered_customers = customers[customers["Location"].isin(selected_locations)]

# Filter sales by customer and date
filtered_sales = sales[
    (sales["CustomerID"].isin(filtered_customers["CustomerID"])) &
    (sales["Date"] >= pd.to_datetime(date_range[0])) &
    (sales["Date"] <= pd.to_datetime(date_range[1]))
]


# KPIs
st.subheader("Key Metrics")
total_revenue = filtered_sales["TotalPrice"].sum()
total_orders = len(filtered_sales)
unique_customers = filtered_sales["CustomerID"].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Orders", total_orders)
col3.metric("Unique Customers", unique_customers)

# Sales by Month
st.subheader("📅 Sales Over Time")
filtered_sales["Month"] = pd.to_datetime(filtered_sales["Date"]).dt.to_period("M")
monthly_sales = filtered_sales.groupby("Month")["TotalPrice"].sum().reset_index()
monthly_sales["Month"] = monthly_sales["Month"].astype(str)

st.line_chart(monthly_sales.set_index("Month"))

# Top Products
st.subheader("🔥 Top-Selling Products")
top_products = (
    filtered_sales.groupby("ProductID")["Quantity"].sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)


top_products = top_products.merge(products, on="ProductID")
st.table(top_products[["Name", "Quantity"]].rename(columns={"Name": "Product", "Quantity": "Units Sold"}))


# Revenue by Customer Location
st.subheader("📍 Revenue by Customer Location")

location_revenue = (
    filtered_sales.merge(customers, on="CustomerID")
    .groupby("Location")["TotalPrice"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

st.bar_chart(location_revenue.set_index("Location"))

# High-Spending Customers
st.subheader("💸 Top 10 High-Spending Customers")

# Join with customer info
high_spenders = (
    filtered_sales.groupby("CustomerID")["TotalPrice"].sum()
    .reset_index()
    .sort_values(by="TotalPrice", ascending=False)
    .head(10)
    .merge(customers, on="CustomerID")
)

high_spenders_display = high_spenders[["Name", "Email", "TotalPrice"]].rename(columns={"TotalPrice": "Total Spent"})

# Show as table
st.table(high_spenders_display)

# Show as bar chart
st.bar_chart(high_spenders.set_index("Name")["TotalPrice"])
