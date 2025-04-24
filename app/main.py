from fastapi import FastAPI
from app.core.config import get_settings
from app.api.routes import router as api_router

settings = get_settings()

app = FastAPI(
    title="Crop Diagnosis Knowledge Graph API",
    description="API for querying crop diagnosis knowledge graph using LangChain",
    version="1.0.0",
    debug=settings.debug
)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Crop Diagnosis Knowledge Graph API"}
from fastapi import UploadFile, File, Form

@app.post("/kg")
async def get_kg(
    image: UploadFile = File(None, description="Hình ảnh cây trồng cần chẩn đoán"),
    text: str = Form(None, description="Mô tả triệu chứng của cây trồng")
):
    if image:
        content = await image.read()

    if text:
        # Xử lý văn bản
        # TODO: Xử lý văn bản ở đây
        return {"message": f"Đã nhận mô tả: {text}"}

    return {"message": "Chào mừng đến với API Đồ thị Tri thức Chẩn đoán Cây trồng"}
