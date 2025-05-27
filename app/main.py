import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from app.core.config import get_settings
from app.api.routes import router as api_router
from app.models.crop_clip import CLIPModule
from app.models.gemini_caller import GeminiGenerator
from app.utils.data_mapping import DataMapping, SingletonModel
from app.models.knowledge_graph import KnowledgeGraphUtils, Neo4jConnection
import asyncio
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()

class ModelLoader:
    def __init__(self):
        self.clip_model = None
        self.gemini_model = None
        self.sentence_transformer = None
        self.neo4j_connection = None

    def load_models(self):
        try:
            if settings.load_clip_model:
                logger.info("Loading CLIP model...")
                self.clip_model = CLIPModule()
                logger.info("CLIP model loaded successfully")

            if settings.load_gemini_model:
                logger.info("Loading Gemini model...")
                self.gemini_model = GeminiGenerator()
                logger.info("Gemini model loaded successfully")

            if settings.load_data_mapper:
                logger.info("Loading DataMapper model...")
                self.data_mapper = DataMapping()
                logger.info("DataMapper model loaded successfully")

            if settings.load_knowledge_graph:
                logger.info("Connecting to Knowledge Graph...")
                self.knowledge_graph = KnowledgeGraphUtils()
                logger.info("Knowledge Graph connection established")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise

    def close(self):
        if self.neo4j_connection:
            logger.info("Closing Neo4j connection...")
            self.neo4j_connection.close()
        self.clip_model = None
        self.gemini_model = None
        self.sentence_transformer = None
        logger.info("Models released")

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, app.state.model_loader.load_models)
    logger.info("Application startup complete")
    yield
    app.state.model_loader.close()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="Crop Diagnosis Knowledge Graph API",
    description="API for querying crop diagnosis knowledge graph using LangChain",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

app.state.model_loader = ModelLoader()

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Crop Diagnosis Knowledge Graph API"}

