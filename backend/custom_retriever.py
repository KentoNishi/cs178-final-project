from langchain.embeddings.base import Embeddings
from langchain_chroma import Chroma
from langchain.schema import BaseRetriever

class CustomRetriever(BaseRetriever):
    embeddings: Embeddings
    chroma: Chroma
    
    def get_relevant_documents(self, query):
        # calculate embeddings for query string
        emb = self.embeddings.embed_query(query)
        option1 = self.chroma.similarity_search_by_vector(embedding=emb)
        return option1
    
    async def aget_relevant_documents(self):
        return []