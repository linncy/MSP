import requests
import sqlite3
import pytz, time
from datetime import datetime

db_name = 'autoscaler_monitor.db'
MA_par=20

def gettime():
	time.time()
	tz  = pytz.timezone('America/Edmonton')
	newdatetime=datetime.fromtimestamp(time.time(), tz)
	format = "%H:%M:%S"
	return(newdatetime.strftime(format))

def create_db():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS response_time')
    c.execute('CREATE TABLE response_time (id INTEGER PRIMARY KEY AUTOINCREMENT, insert_time text,response_time float,ma float)')
    conn.close()

def save_to_db(response_timedata):
    #['00:01',4.16]
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('INSERT INTO response_time(insert_time,response_time,ma) VALUES (?,?,?)', response_timedata)
    conn.commit()
    conn.close()

def monitor():
	responselist=[]
	create_db()
	swarm_master_ip = '10.8.47.180'
	port='443'
	for i in range(MA_par):
		t0 = time.time()
		requests.get('http://' + swarm_master_ip + ':'+port+'/')
		t1 = time.time()
		print("t1-t0=",t1-t0)
		responselist.insert(0,t1-t0)
		tmpsum=0
		for j in range(i+1):
			tmpsum+=responselist[j]
		avg=tmpsum*1.0/(i+1)
		time.sleep(1)
		save_to_db((gettime(),t1-t0,avg))
	while True:
		t0 = time.time()
		requests.get('http://' + swarm_master_ip + ':'+port+'/')
		t1 = time.time()
		print(responselist.pop())
		responselist.insert(0,t1-t0)
		tmpsum=0
		for j in range(MA_par):
			tmpsum+=responselist[j]
		ma=tmpsum*1.0/MA_par
		print('ma=',ma)
		time.sleep(1)
		save_to_db((gettime(),t1-t0,ma))