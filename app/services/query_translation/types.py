from pydantic import BaseModel
from typing import List, Literal


QueryType = Literal["simple","complex","sparse","conceptual"]

class QueryAnalysis(BaseModel):
    query_type: QueryType
    confidence: float

