import os
import sys

from fastapi import Depends
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import Settings, get_settings
from utils.data_mapping import DataMapping
from utils.extract_entity import extract_entities
from core.type import Node
from neo4j import GraphDatabase
from utils.constant import NEO4J_LABELS, NEO4J_RELATIONS

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

class Neo4jConnection:
    def __init__(self):
        """Khởi tạo kết nối tới Neo4j"""
        self.uri = NEO4J_URI
        self.user = NEO4J_USER
        self.password = NEO4J_PASSWORD
        self.database = NEO4J_DATABASE

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

class KnowledgeGraphUtils:
    def get_disease_from_env_factors(self, crop_id: str, params: list[Node]):
        envFactors = [param.id for param in params if param.label == "EnvironmentalFactor"]
        query = f"""
            MATCH (c:Crop {{id: "{crop_id}"}})
            WITH c
            MATCH (d:Disease)-[:AFFECTS]-(c)
            OPTIONAL MATCH (ef:EnvironmentalFactor)-[:FAVORS]-(d)
            WHERE ef.id IN {envFactors}
            OPTIONAL MATCH (ef2:EnvironmentalFactor)-[:FAVORS]-(cause:Cause)-[:CAUSES|AFFECTS]-(d)
            WHERE ef2.id IN {envFactors}
            WITH d, COLLECT(DISTINCT ef.id) AS direct_env, COLLECT(DISTINCT ef2.id) AS indirect_env
            WHERE SIZE(direct_env) > 0 OR SIZE(indirect_env) > 0
            RETURN DISTINCT d.name, d.id, d.description, direct_env AS DirectEnvironmentalFactors, indirect_env AS IndirectEnvironmentalFactors
        """
        kg = Neo4jConnection()
        result = kg.execute_query(query)
        return result

    def get_disease_from_symptoms(self, crop_id: str, params: list[Node]):
        symptoms = [param.id for param in params if param.label == "Symptom"]
        query = f"""
            MATCH (c:Crop {{id: "{crop_id}"}})
            WITH c
            MATCH (d:Disease)-[:AFFECTS]-(c)
            OPTIONAL MATCH (sym1:Symptom)-[:HAS_SYMPTOM]-(d)
            WHERE sym1.id IN {symptoms}
            OPTIONAL MATCH (sym2:Symptom)-[:HAS_SYMPTOM|LOCATED_ON]-(p:PlantPart)-[:CONTAINS]-(d)
            WHERE sym2.id IN {symptoms}
            WITH d, p, c, sym1, sym2, COLLECT(DISTINCT sym1.id) AS direct_env, COLLECT(DISTINCT sym2.id) AS indirect_env
            WHERE SIZE(direct_env) > 0 OR SIZE(indirect_env) > 0
            RETURN d.name ,c.name,p.name, sym1, sym2
        """
        kg = Neo4jConnection()
        result = kg.execute_query(query)
        return result
