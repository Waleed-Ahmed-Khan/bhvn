from send_report import SendReport
import fasteners
import threading 
import sys

thread_lock = threading.Lock() 
def main():
    
    report = SendReport()
    if report.if_locked():
        with open(report.logs_file, 'a+') as file:
            report.logger.log(file, "########### Terminating the job as the file is locked ###########")
        sys.exit(0)
    thread_lock.acquire()
    with fasteners.InterProcessLock(report.lock_file):
        report.send_email()
if __name__ == '__main__':
    main()
thread_lock.release()