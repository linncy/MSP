import urllib3
import json
#requrl = "http://10.8.47.180:5900/api"
requrl = "http://127.0.0.1:5900/api"
def get_lastid(requrl):
	post_data=json.dumps({})
	http = urllib3.PoolManager()
	req = http.request('POST', requrl,
                 headers={'Content-Type': 'application/json'},
                 body=post_data)
	back=json.loads(req.data.decode())
	return back[0]
def get_reponsetime(requrl,id,num):
	post_data=json.dumps({'id':id})
	http = urllib3.PoolManager()
	req = http.request('POST', requrl,
                 headers={'Content-Type': 'application/json'},
                 body=post_data)
	back=json.loads(req.data.decode())
	return back['response'][0:num]

print(get_lastid(requrl))
print(get_reponsetime(requrl,1578,1))
#print(type(back['response'][1]))
#print(post_data)
#print (req.data.decode())