import os
from sentence_transformers import SentenceTransformer
import faiss
from pyvi.ViTokenizer import tokenize
import sqlite3


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
        self.model = SingletonModel().model
        self.index = self.__load_faiss_index()
        conn = sqlite3.connect(VECTOR_EMBEDDINGS_DB_PATH)
        self.cursor = conn.cursor()

    def __load_faiss_index(self, index_file = FAISS_INDEX_PATH):
        if os.path.exists(index_file):
            index = faiss.read_index(index_file)
            print(f"Đã nạp FAISS index từ {index_file}")
            return index
        return None

    def get_top_index_by_text(self, text, top_k = 1):
        q_token = tokenize(text)
        q_vec = self.model.encode([q_token])
        faiss.normalize_L2(q_vec)
        D, I = self.index.search(q_vec, top_k)
        return I[0]

    def get_embedding_by_id(self, id):
        self.cursor.execute("SELECT * FROM embeddings WHERE e_index = ?", (id,))
        return self.cursor.fetchone()

    def get_top_result_by_text(self, text, top_k = 1, type = None):
        top_index = self.get_top_index_by_text(text, top_k)
        results = [self.get_embedding_by_id(int(index)) for index in top_index]
        if type:
            results = [result for result in results if result[3] == type]
        return results

if __name__ == "__main__":
    data_mapping = DataMapping()
    results = data_mapping.get_top_result_by_text("Cây lúa", 10)
    for result in results:
        if result[3] == "Crop":
            print(result[1], result[2])
