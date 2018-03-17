import numpy as np
volume=20
def batch():
    batchdict={}
    for sca in range(8):
        newdict={}
        for req in range(16):
        	fname='sca_'+str(sca)+'req_'+str(req)+'.txt'
        	print(fname)
        	datalist=[]
        	f=open(fname,"r")
        	for item in f:
        		datalist.append(float(item))
        	f.close()
        	adict={'mean':np.mean(datalist),'std':np.std(datalist)}
        	newdict[req]=adict
        batchdict[sca]=newdict
    return batchdict

batchdict=batch()
for sca in range(8):
    newlist=[]
    for req in range(16):
        newlist.append(batchdict[sca][req]['mean'])
    print('sca=',sca,' ',newlist)
