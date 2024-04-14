import chromadb
import os
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from scripts.utils import progbar, load_env
from scripts.config import CONFIG

# Loading .env for OpenAI API key
load_env()

chroma_client = chromadb.PersistentClient(path=CONFIG.vector_db_path)
embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name=CONFIG.embedding_model)
course_collection = chroma_client.get_collection(name=CONFIG.collection_name, embedding_function=embedding_function)

def query_collection(collection, query : str, max_results : int) -> dict[str, str]:
  # Getting the results, removing any where the values are None
  results = {k: v for k, v in collection.query(query_texts=query, n_results=max_results, include=['distances', 'metadatas']).items() if v}

  # Formatting such that key is courseID, value is associated text
  formatted = {}
  for idx in range(len(results['ids'][0])):
    formatted[results['ids'][0][idx]] = results['metadatas'][0][idx]["text"]

  return formatted


results = query_collection(course_collection, "I'm interested in learning about algorithms", 3)
for id, text in results.items():
  print(f"Result courseID: {id}")
  print(f"Associated text: {text}")
