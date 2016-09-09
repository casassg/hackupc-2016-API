import sqlite3
import csv
import sys

############# State to extract ##################
state = str(sys.argv[1])

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

conn = sqlite3.connect('../backend/api/tmp/test.db')
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT * FROM applications WHERE state=?', (state,))

applications = [(appl["id"], appl["name"].encode('utf-8'), appl["email"].encode('utf-8')) for appl in rows]

with open(state+'.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerows(applications)