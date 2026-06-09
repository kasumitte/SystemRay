## Getting Started
**Requirements:**
Python >=3.13, uv (package manager)
```bash
# 1) Install uv (curl https://astral.sh/uv/install.sh | sh)
# 2) Run 'uv sync'
# 3) 'uv run pytest tests/' - for tests 
```

## Structure Overview
| File | Description |
|---|---|
|src/config | paths for database and logs |
|src/database | as you can guess from the name it containes database implementation |
|src/gui | Graphical User Interface (customtkinter) |
|src/models | most of these pydantic models remain unused, but you can use them for further improvement |
|ai/assistant.py | asynchronous AI request |
|ai/prompt.py | prompts for certain modes of request that are described in assistant.py |
|languages/ | contains translations of UI |
|system/cleaner.py | cleaner functionality |
|system/scanner.py | scanning of files and reading of system logs |
|utils/worker.py | background process |

P.S. I know that russian translation doesn't work, because i couldn't figure out how to fix it
