import time
import sqlite3
import numpy as np
import docker

SCALE_APP_NAME='app_web'
actioninterval=17
upperthreshold=3
lowerthreshold=2
lastaction=0
k=2
base_url='tcp://10.8.47.180:6732'
client=docker.DockerClient(base_url,version='1.26')

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

def isSurge(response):
	print('surge!')
	surgeresponselist=[20,10,7,5,4,3,2,2]
	replicas_now=client.services.get(SCALE_APP_NAME).attrs['Spec']['Mode']['Replicated']['Replicas']
	ma2=np.mean(response[-2:])
	replicas_new=int(np.round(surgeresponselist[replicas_now-1]*1.0/ma2*8.0))
	if(replicas_new<replicas_now):
		replicas_new=replicas_now
	if(replicas_new>8):
		replicas_new=8
	print ('new=',replicas_new)
	md=docker.types.ServiceMode('replicated',replicas=replicas_new)
	client.services.get('app_web').update(mode=md)
	lastaction=getlastid()

def isAscend(response):
	print('ascend!')
	replicas_now=client.services.get(SCALE_APP_NAME).attrs['Spec']['Mode']['Replicated']['Replicas']
	replicas_new=replicas_now+1
	md=docker.types.ServiceMode('replicated',replicas=replicas_new)
	client.services.get('app_web').update(mode=md)
	lastaction=getlastid()

def isSurplus(response):
	print('surplus!')
	replicas_now=client.services.get(SCALE_APP_NAME).attrs['Spec']['Mode']['Replicated']['Replicas']
	replicas_new=replicas_now-1
	md=docker.types.ServiceMode('replicated',replicas=replicas_new)
	count=getlastid()
	client.services.get('app_web').update(mode=md)
	time.sleep(0.2) #wait for scaling down containers
	while True:
		sleep(0.2)
		newcount=getlastid()
		if(newcount>=count+2):
			res = query_db("SELECT * FROM response_time WHERE id>=(?)", args=(newcount-2,))
			break
	response=[x[2] for x in res]
	if(response[-1]>upperthreshold or response[-2]>upperthreshold):
		md=docker.types.ServiceMode('replicated',replicas=replicas_now)
		client.services.get('app_web').update(mode=md)
	else:
		lastaction=getlastid()

def plateau():
	return 0

def slump():
	return 0

def classifier():
	time.sleep(5)
	while True:
		time.sleep(0.2)
		count=getlastid()
		res = query_db("SELECT * FROM response_time WHERE id>=(?)", args=(count-10,))
		response=[x[2] for x in res]
		malist=[x[3] for x in res]
		stdlist=[x[4] for x in res]
		#isSurge-------
		if(response[-1]>malist[-1]+k*stdlist[-1] or response[-2]>malist[-2]+k*stdlist[-2] ):
			if(response[-1]>upperthreshold and response[-2]>upperthreshold):
				isSurge(response)
				continue
		#--------------
		#Action Interval
		if(count-lastaction<=actioninterval):
			continue
		#--------------
		#isAscend------
		if(np.min(malist[-5:])>upperthreshold):
			isAscend(response)
		#--------------
		#isSurplus-----
		if(np.max(malist[-5:])<lowerthreshold):
			isSurplus(response)
		#--------------
		if(response[-1]>=malist[-1]+2*stdlist[-1]):
			surge(response,malist,stdlist)




