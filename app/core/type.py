from pydantic import BaseModel
from typing import List, Optional
import json

class Node(BaseModel):
    id: str
    label: str
    name: str
    properties: dict
    score: Optional[float] = None

    @staticmethod
    def map_json_to_node(json_data: dict) -> 'Node':
        node_data = {
            "name": json_data.pop("name") if "name" in json_data else json_data["id"],
            "id": json_data.pop("id"),
            "label": json_data.pop("label"),
            "properties": json_data
        }
        return Node(**node_data)

    @staticmethod
    def data_row_to_node(data_row: list[str], score = None) -> 'Node':
        return Node(
            id=data_row[1],
            name=data_row[2],
            label=data_row[3],
            properties=json.loads(data_row[4]),
            score=score
        )

class Relationship(BaseModel):
    source: str
    target: str
    type: str
    properties: dict

class KnowledgeGraph(BaseModel):
    nodes: List[Node]
    relationships: List[Relationship]

class GraphQuery(BaseModel):
    key: str
    cypher: str
    parameters: Optional[dict] = None
    description: Optional[str] = None
