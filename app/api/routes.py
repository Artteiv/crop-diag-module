from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from app.api.dto.kg_query import KGQueryRequest, KGQueryResponse, QueryContext
from app.core.dependencies import get_all_models, get_clip_model, get_data_mapper
from app.core.type import Node
from app.models.crop_clip import CLIPModule
from app.models.gemini_caller import GeminiGenerator
from app.models.knowledge_graph import KnowledgeGraphUtils
from app.utils.data_mapping import DataMapping
from app.utils.extract_entity import extract_entities

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    context: Optional[List[str]] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

@router.post("/analyze-image")
async def analyze_image(
    image: UploadFile = File(...),
    clip_model: CLIPModule = Depends(get_clip_model)
):
    """Endpoint để phân tích hình ảnh sử dụng CLIP model"""
    content = await image.read()
    # Sử dụng clip_model để phân tích hình ảnh
    # TODO: Implement image analysis
    return {"message": "Image analysis completed"}

@router.post("/analyze")
async def analyze(
    image: UploadFile = File(None),
    text: str = Form(None),
    models: dict = Depends(get_all_models)
):
    """Endpoint để phân tích cả hình ảnh và văn bản"""
    if image:
        content = await image.read()
        clip_model = models["clip_model"]
        # TODO: Implement image analysis with clip_model

    if text:
        gemini_model = models["gemini_model"]
        # TODO: Implement text analysis with gemini_model

    return {"message": "Analysis completed"}

@router.post("/kg-query")
async def query_kg(
    request: KGQueryRequest,
    models: dict = Depends(get_all_models)
):
    """Endpoint để xử lý dữ liệu JSON"""
    try:
        kg: KnowledgeGraphUtils = models["knowledge_graph"]
        if not request.context:
            request.context = QueryContext()
        if request.crop_id:
            request.context.crop_id = request.crop_id
        if request.additional_info:
            request.context.nodes = get_nodes_from_additional_info(request.additional_info, models["data_mapper"])
        return kg.get_disease_from_env_factors(request.context.crop_id, [node for node, distance in request.context.nodes])

    except Exception as e:
        print(e)
        raise e


def get_nodes_from_additional_info(additional_info: str, data_mapper: DataMapping):
    entities = extract_entities(additional_info)
    top_results: list[tuple[Node, float]] = []
    for entity in entities:
        top_result = data_mapper.get_top_result_by_text(entity.name, 3)
        print([(result.name, distance) for result, distance in top_result])
        for result, distance in top_result:
            top_results.append((result, distance))
    return top_results
