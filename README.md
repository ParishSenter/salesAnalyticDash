# salesAnalyticDash

## Overview
`salesAnalyticDash` is a Python-based project that generates fake sales data and stores it in an SQLite database. The generated data includes customers, products, and sales transactions, which can be used for analytics, testing, or prototyping dashboards.

## Features
- Generates fake customer data (name, email, location, join date).
- Generates fake product data (name, category, price).
- Simulates sales transactions with random quantities and total prices.
- Stores all data in an SQLite database (`sales_data.db`).

## Prerequisites
- Python 3.x
- Required Python libraries:
  - `sqlite3` (built-in)
  - `pandas`
  - `faker`
  - `random`
  - `datetime`

Install dependencies using:
pip install pandas faker