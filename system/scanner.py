from pathlib import Path
from src.metrics import bytes_to_readable
import os
import platform
import logging
import subprocess

def _scan_dirs(dirs: list[Path]):
    logging.info("Starting to scan files...")
    
    categories = {
        "Temporary Files": {"files": [], "total_size": 0},
        "Cache": {"files": [], "total_size": 0},
        "System Logs": {"files": [], "total_size": 0}
    }
    
    for dir in dirs:
        if not dir.exists():
                continue
            
        for path in dir.rglob('*'):
            try:
                if path.is_file():
                    file_size = path.stat().st_size
                    suffix = path.suffix.lower()
                    
                    if suffix == ".log":
                        categories["System Logs"]["files"].append(str(path))
                        categories["System Logs"]["total_size"] += file_size
                        
                    elif ".tmp" in suffix:
                        categories["Temporary Files"]["files"].append(str(path))
                        categories["Temporary Files"]["total_size"] += file_size
                        
                    elif suffix in [".bak", ".old"]:
                        categories["Cache"]["files"].append(str(path))
                        categories["Cache"]["total_size"] += file_size
                    
            except PermissionError:
                logging.warning(f"Permission denied to scan '{path}'")
                continue
            except Exception as e:
                logging.warning(f"Error reading '{path}': {e}")
                continue
    
    return categories
    
def search_redundant_files():
    search_dirs_win = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Temp",
        Path(os.environ.get("APPDATA", "")), 
        Path(os.environ.get("TEMP", "")),
        Path("C:/Windows/Temp"),
        Path("C:/Windows/Prefetch")
    ]
    
    search_dirs_unix = [
        Path(os.environ.get("HOME", "")),
        Path(os.environ.get("HOME", "")) / ".cache",
        Path(os.environ.get("HOME", "")) / "Library" / "Caches"
    ]
    
    if platform.system() == "Windows":
        found_files = _scan_dirs(search_dirs_win)
    else:
        found_files = _scan_dirs(search_dirs_unix)

    ui_result = {}
    for key, item in found_files.items():
        if not item["files"]:
            continue
        
        ui_result[key] = {
            "files": item["files"],
            "size": bytes_to_readable(item["total_size"])
        }
    
    return ui_result


def read_sys_logs():
    try:
        if platform.system() == "Windows":
            command = subprocess.run(
                ['wevtutil', 'qe', 'System', '/c:50', '/rd:true', 
                '/q:*[System[(Level=2 or Level=3) and TimeCreated[timediff(@SystemTime) <= 86400000]]]', '/f:text'],
                capture_output=True, check=True, text=True)
            
        elif platform.system() == "Linux":
            command = subprocess.run(["journalctl", "-n", "50", "-p", "2..4", "--since", "24 hours ago"], capture_output=True, check=True, text=True)
        
        elif platform.system() == "Darwin":
            command = subprocess.run(
            "log show --last 24h --predicate 'messageType == error or messageType == fault' | tail -n 50",
            capture_output=True, check=True, text=True, shell=True)
        
        return command.stdout
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Command to get system logs failed with exit code: [{e.returncode}]")
        raise       
        