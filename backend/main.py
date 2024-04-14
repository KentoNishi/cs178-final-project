from fastapi import FastAPI
import chromadb
import os
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from scripts.utils import load_env
from scripts.config import CONFIG
from scripts.query_vector_db import query_collection

# Loading .env for OpenAI API key
load_env()

chroma_client = chromadb.PersistentClient(path=CONFIG.vector_db_path)
embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name=CONFIG.embedding_model)
course_collection = chroma_client.get_collection(CONFIG.collection_name, embedding_function=embedding_function)

app = FastAPI()

@app.get("/query")
async def query(query: str = ""):
    print(query)
    if (len(query) == 0):
        return {"status": 1}

    results : dict[str, str] = query_collection(course_collection, query, 3)

    return {
        "status": 0,
        "results": results
    }