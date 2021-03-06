import sqlite3
import csv
import sys
import json

############# Number of people into this batch ##################
batch_num = int(sys.argv[1])
############# Is this a travel reimbursement batch ##############
with_travel = int(sys.argv[2])

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

def is_appl_travel(appl, travel):
    data = json.loads(appl['data'])
    try:
        print data['needTravelScholarship']
    except Exception:
        print 'no needs travel scholarship'

    print 'Needs travel?'
    print 'needTravelScholarship' in data and int(data['needTravelScholarship'])
    print 
    if travel:

        return 'needTravelScholarship' in data and int(data['needTravelScholarship']) 

    else:
        return 'needTravelScholarship' not in data or int(data['needTravelScholarship'])==0


conn = sqlite3.connect('../backend/api/tmp/test.db')
conn.row_factory = sqlite3.Row

judgements = []

for appl in conn.execute('SELECT * FROM applications'):
    app_id = appl["id"]
    t = (app_id,)
    count = 0
    total_score = 0
    for judgement in conn.execute('SELECT * FROM judgements WHERE app_id=?', t):
        if judgement["rating"] == "better":
            score = 1
        else:
            score = -2
        count += 1
        total_score += score
        if count != 0:
            avg = total_score/count
        else:
            avg = 0

    if appl['state']=='tbd' and is_appl_travel(appl,with_travel):
        judgements.append([app_id, avg, appl["name"].encode('utf-8'), appl["email"].encode('utf-8')])

judgements = sorted(judgements, key=lambda judgement: -judgement[1])

batch = judgements[:batch_num]
for accepted in batch:
    conn.execute("UPDATE applications SET state='accepted' WHERE id=?",(accepted[0],))
conn.commit()

with open('batch.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerows(judgements[:batch_num])