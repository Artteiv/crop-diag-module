import os
from sentence_transformers import SentenceTransformer
import faiss
from pyvi.ViTokenizer import tokenize
import sqlite3
from app.core.type import Node

FAISS_INDEX_PATH = 'app/data/faiss_index.index'
VECTOR_EMBEDDINGS_DB_PATH = 'app/data/vector_embeddings.db'

class SingletonModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonModel, cls).__new__(cls)
            cls._instance.model = SentenceTransformer('dangvantuan/vietnamese-embedding')
        return cls._instance

class DataMapping:
    def __init__(self):
        try:
            self.model: SentenceTransformer = SingletonModel().model
            self.index: faiss.IndexFlatL2 = self.__load_faiss_index()
            self.conn = sqlite3.connect(VECTOR_EMBEDDINGS_DB_PATH, check_same_thread=False)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"Error while initializing DataMapping: {e}")
            raise

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def __load_faiss_index(self, index_file = FAISS_INDEX_PATH):
        if os.path.exists(index_file):
            index = faiss.read_index(index_file)
            print(f"Đã nạp FAISS index từ {index_file}")
            return index
        return None

    def get_top_index_by_text(self, text, top_k=1, distance_threshold=float(0.6)):
        if not text or top_k < 1:
            raise ValueError("Invalid input: text cannot be empty and top_k must be positive")

        q_token = tokenize(text)
        q_vec = self.model.encode([q_token])
        faiss.normalize_L2(q_vec)
        D, I = self.index.search(q_vec, top_k)
        mask = D[0] >= distance_threshold
        filtered_indices = I[0][mask].tolist()
        distances = D[0][mask].tolist()
        return filtered_indices, distances

    def get_embedding_by_id(self, id):
        self.cursor.execute("SELECT * FROM embeddings WHERE e_index = ?", (id,))
        return self.cursor.fetchone()

    def get_top_result_by_text(self, text, top_k = 1, type = None) -> list[Node]:
        top_index, distances = self.get_top_index_by_text(text, top_k)
        results = [self.get_embedding_by_id(int(index)) for index in top_index]
        if type:
            results = [result for result in results if result[3] == type]
        return [Node.data_row_to_node(result, distance) for result, distance in zip(results, distances)]

