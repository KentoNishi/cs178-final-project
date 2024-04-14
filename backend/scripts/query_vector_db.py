import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import pandas as pd
import os
from dotenv import load_dotenv
import openai
import sys

OUTPUT_FOLDER = "../vector_db/"
EMBEDDING_MODEL = "text-embedding-3-small"

# Loading .env for OpenAI API key
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
if os.getenv("OPENAI_API_KEY") is not None:
  openai.api_key = os.getenv("OPENAI_API_KEY")
  print ("OPENAI_API_KEY is ready!")
else:
  print("OPENAI_API_KEY environment variable not found, check .env is setup correctly!")
  sys.exit(1)

chroma_client = chromadb.PersistentClient(path=OUTPUT_FOLDER)

embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name=EMBEDDING_MODEL)
course_collection = chroma_client.get_collection("course_chunks", embedding_function=embedding_function)

def query_collection(collection, query, max_results):
  results = collection.query(query_texts=query, n_results=max_results, include=['distances', 'metadatas'])
  print(results)
  print(f"Course ID found: {results['ids'][0]}, score: {results['distances'][0]}")


query_collection(course_collection, "Test!", 2)

