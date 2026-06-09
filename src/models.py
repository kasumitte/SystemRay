from pydantic import BaseModel
from datetime import datetime

class SystemMetrics(BaseModel):
    """ Metrics validation """
    cpu_percent: float
    ram_used: float
    ram_total: float
    disk_used: float
    disk_free: float
    collected_at: datetime

class ChatMessage(BaseModel):
    """ Format of input to AI assistant """
    role: str       # 'user'/'assistant'
    content: str
    created_at: datetime
    
class AIAnalysisResult(BaseModel):
    """ 
    Format of output from AI assistant, 
    it validates json structure that goes from AI 
    """
    summary: str        # brief description of system's current condition 
    issues: list[str]
    suggestions: list[str]
    risk_level: str         # 'low'/'medium'/'high'    

