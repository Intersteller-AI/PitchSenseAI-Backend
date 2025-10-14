from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class UploadResponse(BaseModel):
    analysisId: str
    status: str
    filePath: str
