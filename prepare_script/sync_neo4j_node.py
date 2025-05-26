import json
import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.models.knowledge_graph import Neo4jConnection
from sentence_transformers import SentenceTransformer
from pyvi.ViTokenizer import tokenize
import faiss
import numpy as np

# Kết nối SQLite
VECTOR_EMBEDDINGS_DB_PATH = 'app/data/vector_embeddings.db'
FAISS_INDEX_PATH = 'app/data/faiss_index.index'

conn = sqlite3.connect(VECTOR_EMBEDDINGS_DB_PATH)
cursor = conn.cursor()

# Tạo bảng embeddings nếu chưa tồn tại
cursor.execute('''
    CREATE TABLE IF NOT EXISTS embeddings (
        e_index INTEGER PRIMARY KEY,
        id TEXT NOT NULL,
        name TEXT NOT NULL,
        label TEXT NOT NULL,
        properties TEXT NOT NULL
    )
''')

def insert_embedding(e_index, id, name, label, properties):
    """Thêm embedding vào SQLite."""
    cursor.execute('''
        INSERT INTO embeddings (e_index, id, name, label, properties)
        VALUES (?, ?, ?, ?, ?)
    ''', (e_index, id, name, label, json.dumps(properties)))
    conn.commit()
    print(f"Đã thêm embedding: {name}")

def update_embedding(embedding_id, id, name, label, properties):
    """Cập nhật embedding trong SQLite."""
    cursor.execute('''
        UPDATE embeddings
        SET id = ?, name = ?, label = ?, properties = ?
        WHERE e_index = ?
    ''', (id, name, label, json.dumps(properties), embedding_id))
    conn.commit()
    print(f"Đã cập nhật embedding ID: {embedding_id}")

def get_all_embeddings():
    """Lấy tất cả embeddings từ SQLite."""
    cursor.execute('SELECT * FROM embeddings')
    return cursor.fetchall()

def get_embedding_by_id(embedding_id):
    """Lấy embedding theo e_index từ SQLite."""
    cursor.execute('SELECT * FROM embeddings WHERE e_index = ?', (embedding_id,))
    return cursor.fetchone()

def save_faiss_index(index, index_file=FAISS_INDEX_PATH):
    """Lưu FAISS index vào file."""
    faiss.write_index(index, index_file)
    print(f"Đã lưu FAISS index vào {index_file}")

def load_faiss_index(index_file=FAISS_INDEX_PATH):
    """Nạp FAISS index từ file."""
    if os.path.exists(index_file):
        index = faiss.read_index(index_file)
        print(f"Đã nạp FAISS index từ {index_file}")
        return index
    return None

def compute_and_save_embeddings(index_file=FAISS_INDEX_PATH):
    """Tính toán embeddings, lưu vào FAISS và đồng bộ metadata vào SQLite."""
    print("Loading model...")
    model = SentenceTransformer('dangvantuan/vietnamese-embedding')
    print("Model loaded")

    # Lấy dữ liệu từ Neo4j
    neo4j = Neo4jConnection()
    result = neo4j.execute_query("MATCH (n) RETURN n")
    corpus = []

    # Chuẩn bị corpus và lưu metadata vào SQLite
    print("Processing Neo4j data and saving to SQLite...")
    for index, record in enumerate(result):
        print(record)
        label = list(record["n"].labels)[0]
        print(label)
        embedding = dict(record["n"])
        id = embedding.pop('id')
        name = embedding.pop('name') if 'name' in embedding else id
        properties = embedding
        corpus.append(name)

        # Kiểm tra và cập nhật/thêm vào SQLite
        cursor.execute('SELECT e_index FROM embeddings WHERE e_index = ?', (index,))
        existing = cursor.fetchone()
        if existing:
            update_embedding(index, id, name, label, properties)
        else:
            insert_embedding(index, id, name, label, properties)

    # Tính toán embeddings
    print("Tokenizing and encoding...")
    tokenized = [tokenize(s) for s in corpus]
    embeddings = model.encode(tokenized, show_progress_bar=False)
    print("Encoding done")

    # Chuẩn hóa embeddings
    print("Normalizing...")
    faiss.normalize_L2(embeddings)
    print("Normalized")

    # Tạo và lưu FAISS index
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(embeddings)
    save_faiss_index(index, index_file)

    print("Processing completed")
    return index, corpus, embeddings

def load_or_compute_embeddings(index_file=FAISS_INDEX_PATH):
    """Nạp hoặc tính toán embeddings và FAISS index."""
    # Thử nạp FAISS index
    index = load_faiss_index(index_file)

    # Lấy corpus từ SQLite
    embeddings_data = get_all_embeddings()
    corpus = [row[2] for row in embeddings_data]  # Lấy cột name

    if index is None or not corpus:
        print("No saved index or corpus found, computing new ones...")
        index, corpus, embeddings = compute_and_save_embeddings(index_file)
    else:
        print("Loaded existing index and corpus")

    return index, corpus

def get_qvec_by_text(model, text):
    q_token = tokenize(text)
    q_vec = model.encode([q_token])
    faiss.normalize_L2(q_vec)
    return q_vec

if __name__ == "__main__":
    try:
        index, corpus = load_or_compute_embeddings()
        print(f"Index ready with {index.ntotal} embeddings, corpus size: {len(corpus)}")
        model = SentenceTransformer('dangvantuan/vietnamese-embedding')
        while True:
            try:
                query = input("Nhập câu truy vấn (nhấn Ctrl+C để thoát): ")
                q_vec = get_qvec_by_text(model, query)
                k = 1  # số kết quả cần lấy
                D, I = index.search(q_vec, k)
                print("Câu truy vấn:", query)
                print(I[0][0])
                print(type(I[0][0]))
                print("Câu gần nhất:", get_embedding_by_id(int(I[0][0])), "(khoảng cách:", D[0][0], ")")
                print("-" * 50)
            except KeyboardInterrupt:
                print("\nĐã dừng chương trình!")
                break
    finally:
        conn.close()
        print("SQLite connection closed")
