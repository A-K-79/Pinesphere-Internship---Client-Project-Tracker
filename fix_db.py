import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# DemoSubmission
cur.execute("UPDATE projects_demosubmission SET advance_payment = 0 WHERE advance_payment = ''")
cur.execute("UPDATE projects_demosubmission SET full_payment = 0 WHERE full_payment = ''")
cur.execute("UPDATE projects_demosubmission SET payment_amount = 0 WHERE payment_amount = ''")

# DemoURL
cur.execute("UPDATE projects_demourl SET advance_payment = 0 WHERE advance_payment = ''")
cur.execute("UPDATE projects_demourl SET full_payment = 0 WHERE full_payment = ''")

conn.commit()
conn.close()
print("Fixed ALL DB decimals")
