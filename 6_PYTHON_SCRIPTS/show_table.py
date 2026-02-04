#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(host="localhost", port=5432, database="charger_db", user="charger_user", password="admin")
cursor = conn.cursor()

# Show all columns for charger_usage_log
cursor.execute("""
    SELECT *
    FROM charger_usage_log
    LIMIT 1
""")

print("Columns in charger_usage_log:")
for i, desc in enumerate(cursor.description):
    print(f"{i+1}. {desc[0]}")

# Get a sample record
cursor.execute("SELECT * FROM charger_usage_log LIMIT 1")
row = cursor.fetchone()
if row:
    print("\nSample record:")
    for i, desc in enumerate(cursor.description):
        print(f"  {desc[0]}: {row[i]}")

cursor.close()
conn.close()
