import time
import sqlite3
import numpy as np
import docker
import pytz
from datetime import datetime

SCALE_APP_NAME='app_web'
actioninterval=17
upperthreshold=3
lowerthreshold=2
global lastaction
global lastsurge
k=2
base_url='tcp://10.8.47.180:6732'
client=docker.DockerClient(base_url,version='1.26')

def gettime():
	time.time()
	tz  = pytz.timezone('America/Edmonton')
	newdatetime=datetime.fromtimestamp(time.time(), tz)
	format = "%H:%M:%S"
	return(newdatetime.strftime(format))

def create_log_db():
    conn = sqlite3.connect('log.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS log')
    c.execute('CREATE TABLE log (id INTEGER PRIMARY KEY AUTOINCREMENT, insert_time text, action text, replicas INTEGER, criterion text, lastactionid INTEGER)')
    conn.close()

def save_to_log_db(logdata):
    #['00:01',4.16]
    conn = sqlite3.connect('log.db')
    c = conn.cursor()
    c.execute('INSERT INTO log(insert_time,action,replicas,criterion,lastactionid) VALUES (?,?,?,?,?)', logdata)
    conn.commit()
    conn.close()

def get_log_db():
    db = sqlite3.connect('log.db')
    db.row_factory = sqlite3.Row
    return db

def query_log_db(query, args=(), one=False):
    db = get_log_db()
    cur = db.execute(query, args)
    db.commit()
    rv = cur.fetchall()
    db.close()
    return (rv[0] if rv else None) if one else rv

def get_log_lastid():
	res=query_log_db("SELECT * FROM sqlite_sequence")
	count=[x[1] for x in res][0]
	return count

def get_db():
    db = sqlite3.connect('autoscaler_monitor.db')
    db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    rv = cur.fetchall()
    db.close()
    return (rv[0] if rv else None) if one else rv

def getlastid():
	res=query_db("SELECT * FROM sqlite_sequence")
	count=[x[1] for x in res][0]
	return count

def isSurge(response,malist,stdlist):
	global lastaction
	global lastsurge
	print('surge!')
	surgeresponselist=[20,10,7,5,4,3,2,2]
	replicas_now=client.services.get(SCALE_APP_NAME).attrs['Spec']['Mode']['Replicated']['Replicas']
	ma2=np.mean(response[-2:])
	replicas_new=int(np.round(ma2*1.0/surgeresponselist[replicas_now-1]*8.0))
	if(replicas_new<replicas_now):
		replicas_new=replicas_now
	if(replicas_new>8):
		replicas_new=8
	print ('new=',replicas_new)
	md=docker.types.ServiceMode('replicated',replicas=replicas_new)
	client.services.get('app_web').update(mode=md)
	lastaction=getlastid()
	lastsurge=lastaction
	cri='Response: '+str(response[-2])+' MA:'+str(np.round(malist[-2:],3).tolist())+' stdev: '+str(np.round(stdlist[-2:],3).tolist())
	save_to_log_db((gettime(),'Scale Up: Surge',replicas_new,cri,lastaction))
	print('lastaction by is Surge',lastaction)

def isAscend(response,malist,stdlist):
	global lastaction
	print('ascend!')
	replicas_now=client.services.get(SCALE_APP_NAME).attrs['Spec']['Mode']['Replicated']['Replicas']
	replicas_new=replicas_now+1
	md=docker.types.ServiceMode('replicated',replicas=replicas_new)
	client.services.get('app_web').update(mode=md)
	lastaction=getlastid()
	cri='min in MA: '+str(np.round(malist[-5:],3).tolist())+ ' > upperthreshold'
	save_to_log_db((gettime(),'Scale Up: Ascend',replicas_new,cri,lastaction))

def isSurplus(response,malist,stdlist):
	global lastaction
	global lastsurge
	print('surplus!')
	replicas_now=client.services.get(SCALE_APP_NAME).attrs['Spec']['Mode']['Replicated']['Replicas']
	if(replicas_now==1):
		print('min replicas!')
		return
	replicas_new=replicas_now-1
	md=docker.types.ServiceMode('replicated',replicas=replicas_new)
	count=getlastid()
	client.services.get('app_web').update(mode=md)
	time.sleep(0.2) #wait for scaling down containers
	while True:
		time.sleep(0.2)
		newcount=getlastid()
		if(newcount>=count+2):
			res = query_db("SELECT * FROM response_time WHERE id>=(?)", args=(newcount-2,))
			break
	newresponse=[x[2] for x in res]
	print('surplus count2=',newresponse)
	if(np.max(newresponse)>upperthreshold):
		md=docker.types.ServiceMode('replicated',replicas=replicas_now)
		client.services.get('app_web').update(mode=md)
		lastaction=getlastid()
		lastsurge=lastaction #prevent isSurge caused by Surplus Try
		cri='max in Response'+str(np.round(newresponse,3).tolist())+ ' > upperthreshold'
		save_to_log_db((gettime(),'Do Nothing: Surplus Cancelled',replicas_now,cri,lastaction))
	else:   
		lastaction=getlastid()
		print('Surplus Confirmed',lastaction)
		cri='max in MA'+str(np.round(malist[-5:],3).tolist())+ ' < lowerreshold'
		save_to_log_db((gettime(),'Scale Down: Surplus',replicas_new,cri,lastaction))
        
def plateau():
	return 0

def slump():
	return 0

def classifier():
	global lastaction
	global lastsurge
	create_log_db()
	save_to_log_db((gettime(),'Initialize','Initialize','Initialize','Initialize'))
	time.sleep(5)
	lastaction=getlastid()
	lastsurge=lastaction
	while True:
		time.sleep(0.2)
		count=getlastid()
		res = query_db("SELECT * FROM response_time WHERE id>=(?)", args=(count-10,))
		response=[x[2] for x in res]
		malist=[x[3] for x in res]
		stdlist=[x[4] for x in res]
		#isSurge-------
		if(count-lastsurge>2):
			if(response[-1]>malist[-1]+k*stdlist[-1] or response[-2]>malist[-2]+k*stdlist[-2] ):
				if(response[-1]>upperthreshold and response[-2]>upperthreshold):
					isSurge(response,malist,stdlist)
					continue
		#--------------
		#Action Interval
		if(count-lastaction<=actioninterval):           
			continue
		#--------------
		#isAscend------
		if(np.min(malist[-5:])>upperthreshold):
			isAscend(response,malist,stdlist)
		#--------------
		#isSurplus-----
		if(np.max(malist[-5:])<lowerthreshold):
			isSurplus(response,malist,stdlist)
		#--------------
if __name__ == "__main__":
    classifier()