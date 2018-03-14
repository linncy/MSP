"""
HTTP client simulator. It simulate a number of concurrent users and calculate the response time for each request.
"""


import time
import threading
import sys
from multiprocessing import Queue
import monitor
import response_visualizer



if __name__ == "__main__":
    mutexA = threading.Lock()
    swarm_master_ip = '10.8.47.180'
    port='443'
    threads = []
    threads.append(threading.Thread(target=monitor.monitor))
    #threads.append(threading.Thread(target=response_visualizer.manager.run()))
    #threads.append(threading.Thread(target=calculator,args=[que]))
    for i in range(len(threads)):
        threads[i].start()
    for i in range(len(threads)):
        threads[i].join()
