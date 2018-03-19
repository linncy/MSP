import time
import threading
import sys
import monitor
import analyzer

if __name__ == "__main__":
    swarm_master_ip = '10.8.47.180'
    port='443'
    threads = []
    threads.append(threading.Thread(target=monitor.monitor))
    #threads.append(threading.Thread(target=analyzer.classifier)) #Disable autoscaling feaature
    for i in range(len(threads)):
        threads[i].start()
    for i in range(len(threads)):
        threads[i].join()
    #threads.append(threading.Thread(target=calculator,args=[que]))