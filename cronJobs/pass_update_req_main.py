from pass_update_req import PassUpdateReq
import fasteners
import threading 
import sys

thread_lock = threading.Lock() 
def main():
    pass_update = PassUpdateReq()
    if pass_update.if_locked():
        with open(pass_update.logs_file, 'a+') as file:
            pass_update.logger.log(file, "########### Terminating the job as the file is locked ###########")
        sys.exit(0)
    thread_lock.acquire()
    with fasteners.InterProcessLock(pass_update.lock_file):
        pass_update.get_weak_pass()
        pass_update.email_delivery()

if __name__ == '__main__':
    main()
thread_lock.release()
    
