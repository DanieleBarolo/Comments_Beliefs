from pydantic import BaseModel
from typing import List, Literal

class OpenTargetResult(BaseModel):
    target: str
    stance: Literal["FAVOR", "AGAINST", "NONE"]
    stance_type: Literal["EXPLICIT", "IMPLICIT"]
    key_claims: List[str]
    explanation: str

class OpenTargetResults(BaseModel):
    results: List[OpenTargetResult]