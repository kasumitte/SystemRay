from src.gui import MainWindow
from utils.worker import Worker, resource_path
from src.config import Conf
from src.database import init_db, init_default_settings, get_settings_by_key
import json
import queue
import os
import customtkinter as ctk

def main():
    path_to_json = resource_path(os.path.join("languages", "translations.json"))
    
    with open(path_to_json, encoding="utf-8") as f:
        TRANSLATIONS = json.load(f)
    config = Conf
    config.init_dirs()
      
    init_db(config.DB_PATH)
    init_default_settings(config.DB_PATH)
    
    language = get_settings_by_key(config.DB_PATH, "language")
    theme = get_settings_by_key(config.DB_PATH, "theme")
    
    ctk.set_appearance_mode(theme[0] if theme else "dark")
    
    task_queue = queue.Queue()
    result_queue = queue.Queue()

    worker = Worker(task_queue, result_queue, config.DB_PATH)
    worker._start_t()
    app = MainWindow(task_queue, result_queue, 
                    translations=TRANSLATIONS, 
                    lang=language[0] if language else "en", 
                    theme=theme[0] if theme else "dark")
    app.mainloop()
    

if __name__ == "__main__":
    main()