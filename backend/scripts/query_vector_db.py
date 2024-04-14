import chromadb
import os
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from utils import progbar, load_env
from config import CONFIG

# Loading .env for OpenAI API key
load_env()

chroma_client = chromadb.PersistentClient(path=CONFIG.vector_db_path)
embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name=CONFIG.embedding_model)
course_collection = chroma_client.get_collection("course_chunks", embedding_function=embedding_function)

def query_collection(collection, query, max_results):
  # Getting the results, removing any where the values are None
  results = {k: v for k, v in collection.query(query_texts=query, n_results=max_results, include=['distances', 'metadatas']).items() if v}

  # Formatting such that key is courseID, value is associated text
  formatted = {}
  for idx in range(len(results['ids'][0])):
    formatted[results['ids'][0][idx]] = results['metadatas'][0][idx]["text"]

  return formatted


query_collection(course_collection, "I'm interested in learning about algorithms", 3)

