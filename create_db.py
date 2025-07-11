import sqlite3

conn = sqlite3.connect('project.db')
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_name TEXT
)
""")

cursor.execute("""
CREATE TABLE SKUs (
    SKU_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    SKU_Name TEXT
)
""")

cursor.execute("""
CREATE TABLE job_requests (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    SKU_ID INTEGER,
    job_description TEXT,
    job_cost REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (SKU_ID) REFERENCES SKUs(SKU_ID)
)
""")

cursor.execute("""
CREATE TABLE pros (
    pros_id INTEGER PRIMARY KEY AUTOINCREMENT
    -- add other fields if needed
)
""")

cursor.execute("""
CREATE TABLE bids (
    bid_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    pros_id INTEGER,
    bid_amount REAL,
    bid_status TEXT,
    bid_date TEXT,
    FOREIGN KEY (job_id) REFERENCES job_requests(job_id),
    FOREIGN KEY (pros_id) REFERENCES pros(pros_id)
)
""")

cursor.execute("""
CREATE TABLE job_notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    message TEXT,
    created_at TEXT,
    FOREIGN KEY (job_id) REFERENCES job_requests(job_id)
)
""")

conn.commit()
conn.close()
