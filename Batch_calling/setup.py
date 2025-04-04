from pydantic import BaseModel
from typing import List

class CommentStanceCT(BaseModel): 
    target: str
    stance: str 
    stance_type: str
    explanation: str

class FullStancesCT(BaseModel): 
    results: List[CommentStanceCT]

class CommentStanceCTN(BaseModel): 
    target: str
    stance: str 
    stance_type: str
    explanation: str

class FullStancesCTN(BaseModel): 
    results: List[CommentStanceCT]

class CommentStanceOT(BaseModel): 
    target: str
    stance: str 
    stance_type: str
    key_claims: List[str]
    explanation: str

class FullStancesOT(BaseModel): 
    results: List[CommentStanceOT]