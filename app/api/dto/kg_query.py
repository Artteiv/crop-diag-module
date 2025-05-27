from typing import List, Optional
from pydantic import BaseModel

from app.core.type import Node

class QueryContext(BaseModel):
    crop_id: Optional[str] = None
    nodes: Optional[List[tuple[Node, float]]] = None

class KGQueryRequest(BaseModel):
    context: Optional[QueryContext] = None
    crop_id: Optional[str] = None
    additional_info: Optional[str] = None

class KGQueryResponse(BaseModel):
    answer: str
    sources: List[str]
