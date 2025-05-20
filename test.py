from langchain_neo4j import Neo4jGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain
import dotenv
import os
dotenv.load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI") or "neo4j://localhost:7687"
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME") or "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD") or "password"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print(GEMINI_API_KEY[:4]+"..."+GEMINI_API_KEY[-4:])
graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD
)

# Khởi tạo LLM với Gemini API
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)

# Tạo chuỗi truy vấn đồ thị
chain = GraphCypherQAChain.from_llm(
    allow_dangerous_requests=True,
    llm=llm,
    graph=graph,
    verbose=True
)


# Đặt câu hỏi
question = "Có những bệnh nào trên cây Lúa nước?"
response = chain.run(question)
print(response)
