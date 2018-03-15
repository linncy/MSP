import requests
import sqlite3
import pytz, time
import numpy as np
from datetime import datetime

db_name = 'autoscaler_monitor.db'
MA_par=10

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
    c.execute('CREATE TABLE response_time (id INTEGER PRIMARY KEY AUTOINCREMENT, insert_time text,response_time float,ma float,var float)')
    conn.close()

def save_to_db(response_timedata):
    #['00:01',4.16]
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('INSERT INTO response_time(insert_time,response_time,ma,var) VALUES (?,?,?,?)', response_timedata)
    conn.commit()
    conn.close()

def monitor():
	responselist=[]
	create_db()
	swarm_master_ip = '10.8.47.180'
	port='443'
	for i in range(MA_par):
		t0 = time.time()
		try:
			requests.get('http://' + swarm_master_ip + ':'+port+'/')
		except:
			pass
		t1=time.time()
		responselist.insert(0,t1-t0)
		time.sleep(1)
		save_to_db((gettime(),t1-t0,np.mean(responselist),np.std(responselist)))
	while True:
		t0 = time.time()
		try:
			requests.get('http://' + swarm_master_ip + ':'+port+'/')
		except:
			pass
		t1=time.time()
		responselist.pop()
		responselist.insert(0,t1-t0)
		time.sleep(1)
		save_to_db((gettime(),t1-t0,np.mean(responselist),np.std(responselist)))