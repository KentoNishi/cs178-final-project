import os

class Config:
  def __init__(self):
    self.vector_db_path = os.path.join(os.path.dirname(__file__), '..', 'vector_db')
    self.embeddings_file = os.path.join(os.path.dirname(__file__), '..', 'embeddings', 'spring25_v2.json')
    self.embedding_model = "text-embedding-3-small"
    self.env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    self.reset_db = True
    self.collection_name = "course_chunks"

CONFIG = Config()