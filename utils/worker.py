import threading
import asyncio
import sys
import os
import sys
import keyring
from queue import Queue
import logging
from logging.handlers import RotatingFileHandler
from src.config import Conf
from pathlib import Path
from ai.assistant import get_AIResponse
from src.database import (
    get_settings_by_key, get_latest_metrics, save_user_settings, get_latest_session_id, get_chat_history
)
from system.cleaner import clean_files
from system.scanner import (search_redundant_files, read_sys_logs)
from src.metrics import collect_metrics


# Set logging levels
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
format = logging.Formatter("[%(asctime)s] [%(levelname)s]: %(message)s")

console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
console.setFormatter(format)

log_path = Conf.LOG_PATH
log_path.parent.mkdir(exist_ok=True, parents=True)

file_log = RotatingFileHandler(log_path,
                            mode="a", encoding="utf-8", maxBytes=2*1024*1024, backupCount=5)
file_log.setLevel(logging.ERROR)
file_log.setFormatter(format)

logger.addHandler(console)
logger.addHandler(file_log)

def resource_path(relative_path):
    """ Get an absolute path to the resource """
    try:
        base_path = sys._MEIPASS # type: ignore
    except Exception:
        base_path = os.path.abspath(".")
        
    return os.path.join(base_path, relative_path)

class Worker:
    def __init__(self, task_queue: Queue, result_queue: Queue, db_path: Path):
        self.db_path = db_path
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.thread = threading.Thread(target=self._run, daemon=True)
    
    def handle_result(self, result):
        match result[0]:
            case "scan":
                self.send_result("update_bar", (0.1, "10%"))
                listed_metrics = collect_metrics(self.db_path)
                self.send_result("update_bar", (0.5, "50%"))
                found_files = search_redundant_files()
                self.send_result("update_bar", (1, "100%"))
                
                self.send_result("scan_done", found_files)
                self.send_result("update_metrics", listed_metrics)
                
            case "clean":
                stats = clean_files(result[1])
                self.send_result("clean_done", stats)  
                
            case "message":
                api_key = get_settings_by_key(self.db_path, "api_key")
                if not api_key or not api_key[0].strip():
                    logger.error("Couldn't find any available API keys in database")
                    self.send_result("no_key")
                    return
                
                syslogs = read_sys_logs()
                metrics = get_latest_metrics(self.db_path)
                
                try:
                    session_id, text = asyncio.run(get_AIResponse(
                        api_key[0], self.db_path, metrics, syslogs, result[1], mode="chat"
                    )) # type: ignore
                    self.send_result("message", text)
                except Exception as e:
                    logger.error(f"AI call failed: {e}")
                    self.send_result("message", "Network error or wrong API key")
                
            case "save_settings":
                keyring.set_password("system", "user", result[1]["api_key"])
                save_user_settings(self.db_path, "api_key", result[1]["api_key"])
                
            case "load_history":
                latest_id = get_latest_session_id(self.db_path)
                if latest_id is not None:
                    history = get_chat_history(self.db_path, latest_id[0])
                    self.send_result("load_history", history)
                else:
                    logger.info("History is empty")
                    self.send_result("load_history", [])
                
    def _run(self):
        while True:
            task = self.task_queue.get()
            self.handle_result(task)

    def _start_t(self):
        self.thread.start()
        
    def send_result(self, task_type, data=None):
        self.result_queue.put((task_type, data))
