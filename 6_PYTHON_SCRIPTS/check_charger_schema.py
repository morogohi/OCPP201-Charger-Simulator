#!/usr/bin/env python3
import os
os.environ['DATABASE_URL'] = 'postgresql://charger_user:admin@localhost:5432/charger_db'

from database.models_postgresql import DatabaseManager
from sqlalchemy import text

db = DatabaseManager()
db.initialize()
session = db.get_session()

result = session.execute(text("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'charger_info'
    ORDER BY ordinal_position
"""))

print('charger_info 칼럼:')
for row in result:
    print(f'  - {row[0]}: {row[1]}')

session.close()
