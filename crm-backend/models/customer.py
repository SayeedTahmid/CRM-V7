from pydantic import BaseModel, EmailStr
from typing import List, Optional
import datetime

class CustomerModel(BaseModel):
    id: str
    companyName: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[str] = "prospect"
    assignedTo: Optional[str] = None
    tags: Optional[List[str]] = []
    createdAt: datetime.datetime
    createdBy: Optional[str] = "system"
