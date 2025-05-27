from fastapi import Depends, Request
from app.models.crop_clip import CLIPModule
from app.utils.data_mapping import DataMapping
from app.models.knowledge_graph import KnowledgeGraphUtils, Neo4jConnection

def get_clip_model(request: Request) -> CLIPModule:
    """Lấy CLIP model từ app.state"""
    return request.app.state.model_loader.clip_model

def get_data_mapper(request: Request) -> DataMapping:
    """Lấy DataMapper từ app.state"""
    return request.app.state.model_loader.data_mapper

def get_knowledge_graph(request: Request) -> KnowledgeGraphUtils:
    """Lấy KnowledgeGraph từ app.state"""
    return request.app.state.model_loader.knowledge_graph

def get_all_models(
    clip_model: CLIPModule = Depends(get_clip_model),
    data_mapper: DataMapping = Depends(get_data_mapper),
    knowledge_graph: KnowledgeGraphUtils = Depends(get_knowledge_graph)
):
    """Lấy tất cả các model từ app.state"""
    return {
        "clip_model": clip_model,
        "data_mapper": data_mapper,
        "knowledge_graph": knowledge_graph
    }
