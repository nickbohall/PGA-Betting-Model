from pydantic import BaseModel
from typing import Optional

class StatusResponse(BaseModel):
    """
    Generic response model for status messages.
    """
    status: str
    message: str
    details: Optional[dict] = None