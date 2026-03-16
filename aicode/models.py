from pydantic import BaseModel, Field
from typing import Optional, List

class ChangeRequest(BaseModel):
    changeId: str = Field(..., alias="change_id")
    apiName: str
    changeType: str
    source: Optional[str] = None   # ✅ ADD THIS
    description: Optional[str] = None

    # Only for schema modification
    xmlPath: Optional[str] = None
    elementName: Optional[str] = None
    attributeName: Optional[str] = None
    datatype: Optional[str] = None
    mandatory: Optional[bool] = None
    allowedValues: Optional[List[str]] = None

    class Config:
        populate_by_name = True
        extra = "allow"   # ✅ SAFE GUARD
