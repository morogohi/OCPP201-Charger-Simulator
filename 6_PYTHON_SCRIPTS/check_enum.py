#!/usr/bin/env python3
import os
os.environ['DATABASE_URL'] = 'postgresql://charger_user:admin@localhost:5432/charger_db'

from database.models_postgresql import DatabaseManager
from sqlalchemy import text

db = DatabaseManager()
db.initialize()
session = db.get_session()

# Enum 타입 확인
result = session.execute(text("""
    SELECT enumlabel FROM pg_enum 
    WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'chargertypeenum')
"""))

print('charger_type Enum 값:')
for row in result:
    print(f'  - {row[0]}')

print()

result = session.execute(text("""
    SELECT enumlabel FROM pg_enum 
    WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'chargerstatusenum')
"""))

print('charger_status Enum 값:')
for row in result:
    print(f'  - {row[0]}')

session.close()
