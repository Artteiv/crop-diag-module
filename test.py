import json
from string import Template
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import Neo4jGraph
import dotenv
import os


from app.models.gemini_caller import GeminiGenerator
from app.models.knowledge_graph import KnowledgeGraph, Neo4jConnection, Node, map_json_to_node
from app.utils.prompt import EXTRACT_ENTITIES_PROMPT
dotenv.load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI") or "neo4j://localhost:7687"
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME") or "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD") or "password"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print(GEMINI_API_KEY[:4]+"..."+GEMINI_API_KEY[-4:])

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)

def extract_entities(text: str) -> list[Node]:
    try:
        gemini = GeminiGenerator()
        prompt = Template(EXTRACT_ENTITIES_PROMPT).substitute(ctext=text)
        entities = gemini.generate(prompt)
        entities = (json.loads(clean_text(entities.text)))["entities"]
        return [map_json_to_node(entity) for entity in entities]
    except Exception as e:
        print(f"Error while extract knowledge entities: {str(e)}")
        return []

def clean_text(text: str):
  text = text.replace("```json", "").replace("```", "")
  return text

graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD
)

def get_disease_from_env_factors(crop_id: str, params: list[Node]):
    envFactors = [param.id for param in params if param.label == "EnvironmentalFactor"]
    # symptoms = [param.id for param in params if param.label == "Symptom"]
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

def get_disease_from_symptoms(crop_id: str, params: list[Node]):
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

text = "Thời tiết gần đây nóng ẩm, đổ mưa nhiều"
result = extract_entities(text)
print(result)
