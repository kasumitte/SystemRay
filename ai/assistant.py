import httpx
import logging
import uuid
import json
from functools import wraps
from ai.prompt import DEFAULT_PROMPT, CHAT_PROMPT
from src.models import AIAnalysisResult
from src.database import save_chat_history, get_settings_by_key
from pydantic import ValidationError
from pathlib import Path
import asyncio

def async_retry(retries=3, delay=4):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try: 
                    return await func(*args, **kwargs)
                except Exception:
                    if attempt == retries:
                        logging.error(f"All {retries} attempts to connect failed")
                        raise
                    await asyncio.sleep(retries * delay)
        return wrapper
    return decorator


@async_retry(retries=3, delay=4)
async def get_AIResponse(api_key: str, db_path: Path, metrics: list, sys_logs: str, request: str, mode="chat"):
    """ Output format -> (session_id, AI response).
        Parameter 'mode' enables you to switch modes of request to AI 
        ('analyze' -> sends metrics, receives json structure; 'chat' - > response for chat.
        'chat' mode by default)
    """  
    session_id = str(uuid.uuid4())
    custom = get_settings_by_key(db_path, "custom_prompt")
    
    # Define prompt for specific mode
    analyze_prompt = custom[0] if custom and custom[0] else DEFAULT_PROMPT
    final_prompt = CHAT_PROMPT if mode == 'chat' else analyze_prompt
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": final_prompt},
            {"role": "user", "content": f"Metrics: [{json.dumps(metrics)}]\nSystem Logs: {json.dumps(sys_logs)}\nUser's request: {request}"}
        ]
    }
    save_chat_history(
        db_path, "user", request, session_id
    )
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, headers=headers, json=payload)
            data = resp.json()['choices'][0]['message']['content']
            save_chat_history(db_path, 'assistant', data, session_id)
            
            # Mode 'chat' returns raw response from AI to GUI chat 
            if mode == 'analyze':
                parsed = json.loads(data)
                validated_data = AIAnalysisResult.model_validate(parsed)
                return session_id, validated_data
            else:
                return session_id, data
            
        except httpx.ConnectError:
            logging.error("Attempt to connect failed")
            raise
        except httpx.HTTPStatusError:
            logging.error("Couldn't establish connection, 4xx or 5xx raised")
            raise
        except httpx.UnsupportedProtocol:
            logging.error("Unsupported protocol for AI")
            raise
        except ValidationError:
            logging.error("Couldn't validate the given data")
            raise
