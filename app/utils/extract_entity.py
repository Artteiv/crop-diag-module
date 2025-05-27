import json
from string import Template
from fastapi import Depends
from langchain_google_genai import ChatGoogleGenerativeAI
import dotenv
import os
from app.models.gemini_caller import GeminiGenerator
from app.core.type import Node
from app.utils.prompt import EXTRACT_ENTITIES_PROMPT
dotenv.load_dotenv()

def extract_entities(text: str) -> list[Node]:
    try:
        gemini = GeminiGenerator()
        prompt = Template(EXTRACT_ENTITIES_PROMPT).substitute(ctext=text)
        entities = gemini.generate(prompt)
        entities = (json.loads(clean_text(entities.text)))["entities"]
        return [Node.map_json_to_node(entity) for entity in entities]
    except Exception as e:
        print(f"Error while extract knowledge entities: {str(e)}")
        return []

def clean_text(text: str):
  text = text.replace("```json", "").replace("```", "")
  return text
