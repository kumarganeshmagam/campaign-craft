from typing import List, Optional
from pydantic import BaseModel

class TargetContact(BaseModel):
    name: str
    role: Optional[str]
    company: Optional[str]
    contact_link: Optional[str]

class UseCase(BaseModel):
    id: str
    title: str
    summary: str
    value_prop: str

class Campaign(BaseModel):
    id: str
    topic: str
    plan: Optional[dict]
    use_cases: Optional[List[UseCase]]
    contacts: Optional[List[TargetContact]]

class Proposal(BaseModel):
    id: str
    title: str
    body: str
