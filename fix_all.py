import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
tables_and_fields = {
    'projects_client': ['revenue_paid', 'revenue_pending', 'satisfaction'],
    'projects_project': ['budget_amount'],
}
for table, fields in tables_and_fields.items():
    for f in fields:
        cur.execute(f"UPDATE {table} SET {f} = 0 WHERE {f} = '' OR {f} IS NULL")

conn.commit()
conn.close()
print("Fixed related decimals")
