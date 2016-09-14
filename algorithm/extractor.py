import sqlite3
import csv
import sys
import json

############# State to extract ##################
state = str(sys.argv[1])

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

def need_travel(obj):
	data = json.loads(obj['data'])
	if 'needTravelScholarship' in data and data['needTravelScholarship'] == '1':
		return 'travel'
	else:
		return 'free'

def is_adult(obj):
	data = json.loads(obj['data'])
	if 'adult' in data and data['adult'] == '1':
		return 'adult'
	else:
		return 'minor'


conn = sqlite3.connect('../backend/api/tmp/test.db')
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT * FROM applications WHERE state=?', (state,))

applications = [(appl["id"], appl["name"].encode('utf-8'), appl["email"].encode('utf-8'), need_travel(appl), is_adult(appl)) for appl in rows]

with open(state+'.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerows(applications)