import os
import subprocess
import platform
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='imagesdel.log',
                    filemode='w')

def get_diskusage(dir_name):
    disk_usage_percent = None
    test_dir = os.path.abspath(dir_name)
    if  Path(test_dir).exists():
        disk_status = shutil.disk_usage(dir_name)
        print(disk_status)
        disk_total = disk_status.total
        disk_used = disk_status.used
        disk_usage_percent = disk_used / disk_total
    return disk_usage_percent

def clean_images():
    cmd = ["docker system prune -a -f"]
    print("cleaning docker images")
    logging.info("cleaning docker images")
    try:
        subp = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE,encoding="utf-8")
        out,error = subp.communicate()
        print(out)
        if subp.returncode == 0:
            logging.info(out)
        else:
            logging.error(error)
    except Exception as e:
        logging.error(e)

# def clean_logs():
    
   
if __name__ == "__main__":
    fdisk = get_diskusage("/")
    logging.info("disk usage {}".format(fdisk))
    if fdisk >= 0.01:
        clean_images()
        print("disk usage is more than 80%")
        logging.info("disk usage is more than 80%")
    else:
        print("disk usage is less than 80%")
        logging.info("disk usage is less than 80%")