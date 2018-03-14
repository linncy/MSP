"""
HTTP client simulator. It simulate a number of concurrent users and calculate the response time for each request.
"""

import requests
import time
import threading
import sys
from multiprocessing import Queue

if len(sys.argv) < 4:
    print('To few arguments; you need to specify 3 arguments.')
    print('Default values will be used for server_ip, no of users and think time.\n')
    swarm_master_ip = '10.8.47.180'  # ip address of the Swarm master node
    no_users = 1  # number of concurrent users sending request to the server
    think_time = 1  # the user think time (seconds) in between consequent requests
else:
    print('Default values have be overwritten.')
    swarm_master_ip = sys.argv[1]
    no_users = int(sys.argv[2])
    think_time = float(sys.argv[3])


class MyThread(threading.Thread):
    def __init__(self, name, counter,que):
        threading.Thread.__init__(self)
        self.threadID = counter
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name + str(self.counter))
        workload(self.name + str(self.counter),que)


def workload(user,que):
    while True:
        t0 = time.time()
        requests.get('http://' + swarm_master_ip + ':443/')
        t1 = time.time()
        time.sleep(think_time)
        #que.put(t1 - t0)
        print("Response Time for " + user + " = " + str(t1-t0))

if __name__ == "__main__":
    que=Queue(maxsize=20)
    threads = []
    for i in range(no_users):
        threads.append(MyThread("User", i ,que))

    for i in range(no_users):
        threads[i].start()

    for i in range(no_users):
        threads[i].join()
