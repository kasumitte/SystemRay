from pathlib import Path
import logging
import hashlib

def clean_files(selected_files: list):
    """ Output format -> {"paths": ..., "stats": (count of deleted paths, freed_space)} """
    deleted_paths = []
    freed_space = 0
    for file in selected_files:
        p = Path(file)
        
        if p.is_file():
            try:
                freed_space += p.stat().st_size
                p.unlink()
                deleted_paths.append(str(p))
            except Exception as e:
                logging.error(f"Error while deleting '{file}' occurred")
                pass
            
    logging.info("Selected files were cleaned")
    return {"paths": deleted_paths, "stats": (len(deleted_paths), freed_space)}

def search_for_duplicates(files: list[Path]):
    hashes = {}
    for path in files:
        h = hashlib.md5(path.read_bytes()).hexdigest()
        hashes.setdefault(h, []).append(path)
    
    return {h: paths for h, paths in hashes.items() if len(paths) > 1}
    