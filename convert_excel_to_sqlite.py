import pandas as pd
import sqlite3

# Read the Excel file
df = pd.read_excel('students.xlsx')

# Connect to SQLite database
conn = sqlite3.connect('students.db')

# Write the DataFrame to the SQLite table
df.to_sql('students', conn, if_exists='replace', index=False)

conn.close()
