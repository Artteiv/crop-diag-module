import json
import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch
from PIL import Image
import clip
import faiss
import numpy as np
import glob

# Đường dẫn lưu trữ
VECTOR_EMBEDDINGS_DB_PATH = 'app/data/vector_embeddings.db'
IMAGE_FAISS_INDEX_PATH = 'app/data/image_faiss_index.index'
TEXT_FAISS_INDEX_PATH = 'app/data/text_faiss_index.index'

# Đường dẫn dữ liệu
DATA_ROOT = '/Users/artteiv/Desktop/Graduated/chore-graduated/Data'
MAIN_DATA_PATH = os.path.join(DATA_ROOT, 'main_data')
CAPTIONS_PATH = os.path.join(DATA_ROOT, 'captions')

# Kết nối SQLite
conn = sqlite3.connect(VECTOR_EMBEDDINGS_DB_PATH)
cursor = conn.cursor()

# Tạo bảng embeddings cho ảnh và văn bản
cursor.execute('''
    CREATE TABLE IF NOT EXISTS image_embeddings (
        e_index INTEGER PRIMARY KEY,
        image_path TEXT NOT NULL,
        caption TEXT NOT NULL,
        category TEXT NOT NULL,
        subcategory TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS text_embeddings (
        e_index INTEGER PRIMARY KEY,
        text TEXT NOT NULL,
        category TEXT NOT NULL,
        subcategory TEXT NOT NULL
    )
''')

def insert_image_embedding(e_index, image_path, caption, category, subcategory):
    """Thêm embedding ảnh vào SQLite."""
    cursor.execute('''
        INSERT INTO image_embeddings (e_index, image_path, caption, category, subcategory)
        VALUES (?, ?, ?, ?, ?)
    ''', (e_index, image_path, caption, category, subcategory))
    conn.commit()
    print(f"Đã thêm embedding ảnh: {image_path}")

def insert_text_embedding(e_index, text, category, subcategory):
    """Thêm embedding văn bản vào SQLite."""
    cursor.execute('''
        INSERT INTO text_embeddings (e_index, text, category, subcategory)
        VALUES (?, ?, ?, ?)
    ''', (e_index, text, category, subcategory))
    conn.commit()
    print(f"Đã thêm embedding văn bản: {text[:50]}...")

def save_faiss_index(index, index_file):
    """Lưu FAISS index vào file."""
    faiss.write_index(index, index_file)
    print(f"Đã lưu FAISS index vào {index_file}")

def load_faiss_index(index_file):
    """Nạp FAISS index từ file."""
    if os.path.exists(index_file):
        index = faiss.read_index(index_file)
        print(f"Đã nạp FAISS index từ {index_file}")
        return index
    return None

def compute_embeddings():
    """Tính toán embeddings cho ảnh và văn bản sử dụng CLIP."""
    print("Loading CLIP model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)
    print("Model loaded")

    # Lấy danh sách các thư mục con (categories)
    categories = [d for d in os.listdir(MAIN_DATA_PATH) if os.path.isdir(os.path.join(MAIN_DATA_PATH, d))]

    image_paths = []
    captions = []
    texts = []
    categories_list = []
    subcategories_list = []

    # Chuẩn bị dữ liệu
    print("Processing data from directories...")
    for category in categories:
        # Đường dẫn đến thư mục category
        category_path = os.path.join(MAIN_DATA_PATH, category)

        # Lấy danh sách các subcategories
        subcategories = [d for d in os.listdir(category_path) if os.path.isdir(os.path.join(category_path, d))]

        for subcategory in subcategories:
            # Đường dẫn đến thư mục ảnh và caption của subcategory
            subcategory_image_path = os.path.join(category_path, subcategory)
            subcategory_caption_path = os.path.join(CAPTIONS_PATH, category, subcategory)


            # Lấy danh sách ảnh
            image_files = glob.glob(os.path.join(subcategory_image_path, '*.*'))

            for img_path in image_files:
                # Lấy tên file không có phần mở rộng
                base_name = os.path.splitext(os.path.basename(img_path))[0]
                caption_file = os.path.join(subcategory_caption_path, f"{base_name}.txt")

                if os.path.exists(caption_file):
                    try:
                        # Đọc caption
                        with open(caption_file, 'r', encoding='utf-8') as f:
                            caption = f.read().strip()

                        # Thêm vào danh sách
                        image_paths.append(img_path)
                        captions.append(caption)
                        texts.append(caption)  # Sử dụng caption làm text
                        categories_list.append(category)
                        subcategories_list.append(subcategory)

                    except Exception as e:
                        print(f"Error processing {img_path}: {e}")
                        continue

    # Tính toán embeddings cho ảnh
    # if image_paths:
    #     print("Computing image embeddings...")
    #     image_embeddings = []
    #     for idx, img_path in enumerate(image_paths):
    #         try:
    #             image = preprocess(Image.open(img_path)).unsqueeze(0).to(device)
    #             with torch.no_grad():
    #                 image_features = model.encode_image(image)
    #                 image_features = image_features.cpu().numpy()
    #                 faiss.normalize_L2(image_features)
    #                 image_embeddings.append(image_features[0])
    #                 insert_image_embedding(idx, img_path, captions[idx], categories_list[idx], subcategories_list[idx])
    #         except Exception as e:
    #             print(f"Error processing image {img_path}: {e}")
    #             continue

    #     if image_embeddings:
    #         image_embeddings = np.array(image_embeddings)
    #         d = image_embeddings.shape[1]
    #         image_index = faiss.IndexFlatIP(d)
    #         image_index.add(image_embeddings)
    #         save_faiss_index(image_index, IMAGE_FAISS_INDEX_PATH)

    # Tính toán embeddings cho văn bản
    if texts:
        print("Computing text embeddings...")
        text_tokens = clip.tokenize(texts, truncate=True).to(device)
        print("Kích thước của text_tokens:", text_tokens.shape)
        with torch.no_grad():
            text_features = model.encode_text(text_tokens)
            text_features = text_features.cpu().numpy()
            faiss.normalize_L2(text_features)

            d = text_features.shape[1]
            text_index = faiss.IndexFlatIP(d)
            text_index.add(text_features)

            # Lưu text embeddings vào SQLite
            for idx, (text, category, subcategory) in enumerate(zip(texts, categories_list, subcategories_list)):
                insert_text_embedding(idx, text, category, subcategory)

            save_faiss_index(text_index, TEXT_FAISS_INDEX_PATH)

    print("Processing completed")
    return image_index if image_paths else None, text_index if texts else None

def predict_image(image_path):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = model.encode_image(image)
        image_features = image_features.cpu().numpy()
        faiss.normalize_L2(image_features)

    index = load_faiss_index(IMAGE_FAISS_INDEX_PATH)
    distances, indices = index.search(image_features, k=10)

    return distances, indices

if __name__ == '__main__':
    ## Predict

    try:
        image_index, text_index = compute_embeddings()
        if image_index:
            print(f"Image index ready with {image_index.ntotal} embeddings")
        if text_index:
            print(f"Text index ready with {text_index.ntotal} embeddings")
    finally:
        conn.close()
        print("SQLite connection closed")
