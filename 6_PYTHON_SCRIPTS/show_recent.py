#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(host="localhost", port=5432, database="charger_db", user="charger_user", password="admin")
cursor = conn.cursor()

# Count records
cursor.execute("SELECT COUNT(*) FROM charger_usage_log")
total = cursor.fetchone()[0]
print(f"Total usage records in database: {total}")

# Get recent records
cursor.execute("""
    SELECT charger_id, transaction_id, energy_delivered, total_charge, created_at
    FROM charger_usage_log
    ORDER BY created_at DESC
    LIMIT 10
""")

print("\nRecent 10 records:")
print("-" * 100)
for row in cursor.fetchall():
    print(f"Charger: {row[0]:20} | Txn: {row[1]:30} | Energy: {row[2]:8.2f} kWh | "
          f"Charge: {row[3]:10.2f} | Time: {row[4]}")

cursor.close()
conn.close()
