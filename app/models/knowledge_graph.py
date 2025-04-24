from pydantic import BaseModel
from typing import List, Optional

class Node(BaseModel):
    id: str
    label: str
    properties: dict

class Relationship(BaseModel):
    source: str
    target: str
    type: str
    properties: dict

class KnowledgeGraph(BaseModel):
    nodes: List[Node]
    relationships: List[Relationship]

class GraphQuery(BaseModel):
    cypher: str
    parameters: Optional[dict] = None
