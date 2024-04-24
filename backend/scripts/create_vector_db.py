import pandas as pd
import os
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from utils import load_env, progbar
from config import CONFIG
import sys

'''
Configuration
'''

# Loading .env for OpenAI API key
load_env()

# Setup embedding function and chroma client
embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name=CONFIG.embedding_model)
chroma_client = chromadb.PersistentClient(path=CONFIG.vector_db_path)

# Reset db if required
if (CONFIG.reset_db):
  if (input("Enter exactly CONFIRM if you wish to reset the database: ") == "CONFIRM"):
    if chroma_client.reset():
      print("Reset vector database successfully")
    else:
      print("Vector database failed to reset properly")
      sys.exit(1)

def safe_str(maybe_str):
  return maybe_str if maybe_str else ""

embedding_id = 0
# Bringing in the data
for file in CONFIG.embeddings_files:
  df = pd.read_json(file, lines=True).T

  # Collections
  try:
    course_collection = chroma_client.get_collection(name=CONFIG.collection_name, embedding_function=embedding_function)
  except ValueError:
    course_collection = chroma_client.create_collection(name=CONFIG.collection_name, embedding_function=embedding_function)

  # Add all the embeddings!
  for courseID, course_data in df.iterrows():
    embedding_data = course_data[0]
    for chunk in embedding_data:
      course_collection.add(
        ids = [str(embedding_id)],
        embeddings = chunk["embedding"],
        metadatas = [{
          "text": chunk["text"],
          "type": chunk["type"],

          # To identify course, to be able to find other data via SQL
          "courseID": courseID,

          # To quickly have these for explainability without needing SQL query
          "courseNumber": chunk["courseNumber"],
          "courseTitle":  chunk["courseTitle"],

          # For filtering
          "termDescription":                      safe_str(chunk["termDescription"]),
          "catalogSubject":                       safe_str(chunk["catalogSubject"]),
          "classLevelAttributeDescription":       safe_str(chunk["classLevelAttributeDescription"]),
          "crossRegistrationEligibleAttribute":   safe_str(chunk["crossRegistrationEligibleAttribute"]),
          "divisionalDistribution":               safe_str(chunk["divisionalDistribution"]),
          "quantitativeReasoning":                safe_str(chunk["quantitativeReasoning"]),

          # TODO: Handle formatting the meetings in a better way to be able to filter by these effectively
          # "meetings": chunk["meetings"]
        }]
      )
      embedding_id += 1