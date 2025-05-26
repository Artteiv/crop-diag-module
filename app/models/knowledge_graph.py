import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pydantic import BaseModel
from typing import List, Optional
from neo4j import GraphDatabase
from utils.constant import NEO4J_LABELS, NEO4J_RELATIONS

class Node(BaseModel):
    id: str
    label: str
    properties: dict

def map_json_to_node(json_data: dict) -> Node:
    node_data = {
        "id": json_data.pop("id"),
        "label": json_data.pop("label"),
        "properties": json_data
    }
    return Node(**node_data)

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

from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "dhruv314")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


class Neo4jConnection:
    def __init__(self, uri=None, user=None, password=None, database=None):
        """Khởi tạo kết nối tới Neo4j"""
        self.uri = uri or NEO4J_URI
        self.user = user or NEO4J_USER
        self.password = password or NEO4J_PASSWORD
        self.database = database or NEO4J_DATABASE

        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password),
            database=self.database
        )
        self.entity_types = []
        self.relations = []

        with self.driver.session() as session:
            result = session.run("CALL db.info()")
            self.database_info = result.single().data()
        self.entity_types = NEO4J_LABELS
        self.relations = NEO4J_RELATIONS

    def get_database_info(self):
        """Trả về thông tin về database đang kết nối"""
        return self.database_info

    def close(self):
        """Đóng kết nối tới Neo4j"""
        if self.driver is not None:
            self.driver.close()

    def execute_query(self, query, parameters=None):
        """Thực thi một truy vấn Cypher bất kỳ"""
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]
