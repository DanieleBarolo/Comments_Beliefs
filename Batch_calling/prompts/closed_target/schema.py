from pydantic import BaseModel
from typing import List, Literal

class ClosedTargetResult(BaseModel):
    target: str
    stance: Literal["FAVOR", "AGAINST", "NONE", "NOT RELATED"]
    stance_type: Literal["EXPLICIT", "IMPLICIT", "NONE"]
    explanation: str

class ClosedTargetResults(BaseModel):
    results: List[ClosedTargetResult]