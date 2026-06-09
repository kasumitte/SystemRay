from src.database import save_coll_metrics, clean_old_metrics
from pathlib import Path
import platform
import psutil
import uuid
import logging

def bytes_to_readable(bytes_val: float):
    """ Display size with measurements for UI """
    if bytes_val >= 1024 ** 3:
        val = round(bytes_val / 1024 ** 3, 2)
        return f"{val} GB"
    elif bytes_val >= 1024 ** 2:
        val = round(bytes_val / 1024 ** 2, 2)
        return f"{val} MB"
    else:
        val = round(bytes_val / 1024, 2)
        return f"{val} KB"


def collect_metrics(db_path: Path):
    logging.info("Starting to collect metrics...")
    scan_id = str(uuid.uuid4())
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        ram_used = psutil.virtual_memory().used
        ram_total = psutil.virtual_memory().total
        ram_perc = psutil.virtual_memory().percent
        
        if platform.system() == "Linux" or platform.system() == "Darwin":
            disk_used = psutil.disk_usage("/").used
            disk_free = psutil.disk_usage("/").free
            disk_perc = psutil.disk_usage("/").percent
            
        elif platform.system() == "Windows":
            disk_used = psutil.disk_usage("C:").used
            disk_free = psutil.disk_usage("C:").free
            disk_perc = psutil.disk_usage("C:").percent
        
        save_coll_metrics(db_path, scan_id, cpu_percent, ram_used, ram_total, disk_used, disk_free)
        clean_old_metrics(db_path) 
        return scan_id, cpu_percent, round(ram_perc, 1), round(disk_perc, 1) 
           
    except psutil.AccessDenied:
        logging.error("Access to collect metrics was denied, check your system's permissions")
          