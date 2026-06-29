import sqlite3
import decimal

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()

for table in tables:
    table_name = table[0]
    cur.execute(f"PRAGMA table_info({table_name})")
    columns = cur.fetchall()
    
    decimal_cols = []
    for col in columns:
        col_type = col[2].upper()
        # In Django, DecimalField in sqlite is usually stored as decimal or varchar
        if 'DECIMAL' in col_type or 'VARCHAR' in col_type:
            decimal_cols.append(col[1])
            
    if not decimal_cols:
        continue
        
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    for row in rows:
        for i, val in enumerate(row):
            if isinstance(val, str) and val == '':
                # If this column is supposed to be decimal
                col_name = columns[i][1]
                print(f"Empty string found in {table_name}.{col_name} for row id={row[0]}")
                
conn.close()
