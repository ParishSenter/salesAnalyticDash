import sqlite3
import pandas as pd
import random
import time
from faker import Faker
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

fake = Faker()
geolocator = Nominatim(user_agent="sales-dashboard")
city_coords_cache = {}

def get_lat_lon(city):
    if city in city_coords_cache:
        return city_coords_cache[city]
    try:
        location = geolocator.geocode(city)
        time.sleep(1)  # Respect rate limits
        if location:
            city_coords_cache[city] = (location.latitude, location.longitude)
            return location.latitude, location.longitude
    except:
        return None, None
    return None, None

# Connect to SQLite database (or create it)
conn = sqlite3.connect("sales_data.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS Customers (
    CustomerID INTEGER PRIMARY KEY,
    Name TEXT,
    Email TEXT,
    Location TEXT,
    JoinDate TEXT,
    Latitude REAL,
    Longitude REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Products (
    ProductID INTEGER PRIMARY KEY,
    Name TEXT,
    Category TEXT,
    Price REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Sales (
    TransactionID INTEGER PRIMARY KEY,
    CustomerID INTEGER,
    ProductID INTEGER,
    Date TEXT,
    Quantity INTEGER,
    TotalPrice REAL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
)
""")

# Generate Customers
customers = []
for _ in range(100):  # Generate 100 customers
    city = fake.city()
    lat, lon = get_lat_lon(city)
    join_date = fake.date_between(start_date="-2y", end_date="today").strftime("%Y-%m-%d")
    customers.append((
        fake.name(),
        fake.email(),
        city,
        join_date,
        lat,
        lon
    ))

cursor.executemany("""
    INSERT INTO Customers (Name, Email, Location, JoinDate, Latitude, Longitude)
    VALUES (?, ?, ?, ?, ?, ?)
""", customers)

# Generate Products
categories = ["Electronics", "Clothing", "Home & Kitchen", "Books", "Toys"]
products = []
for _ in range(20):  # Generate 20 products
    products.append((
        fake.word().capitalize(),
        random.choice(categories),
        round(random.uniform(10, 500), 2)
    ))

cursor.executemany("INSERT INTO Products (Name, Category, Price) VALUES (?, ?, ?)", products)

# Fetch generated customers and products for Sales table
cursor.execute("SELECT CustomerID FROM Customers")
customer_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT ProductID, Price FROM Products")
product_data = cursor.fetchall()

# Generate Sales
sales = []
for _ in range(500):  # Generate 500 sales transactions
    customer_id = random.choice(customer_ids)
    product_id, price = random.choice(product_data)
    date = fake.date_between(start_date="-1y", end_date="today").strftime("%Y-%m-%d")
    quantity = random.randint(1, 5)
    total_price = round(quantity * price, 2)
    
    sales.append((customer_id, product_id, date, quantity, total_price))

cursor.executemany("""
    INSERT INTO Sales (CustomerID, ProductID, Date, Quantity, TotalPrice)
    VALUES (?, ?, ?, ?, ?)
""", sales)

# Commit and close
conn.commit()
conn.close()

print("Fake sales data successfully generated and stored in sales_data.db")
