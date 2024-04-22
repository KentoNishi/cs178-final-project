from langchain.tools import Tool
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.embeddings.base import Embeddings
from langchain.schema import BaseRetriever
from dotenv import load_dotenv

# load OPENAI_API_KEY
load_dotenv()

class CustomRetriever(BaseRetriever):
    embeddings: Embeddings
    chroma: Chroma
    
    def get_relevant_documents(self, query):
        # calculate embeddings for query string
        emb = self.embeddings.embed_query(query)
        option1 = self.chroma.similarity_search_by_vector(
            embedding=emb,
            k=6,
           )
        return option1
    
    async def aget_relevant_documents(self):
        return []


embedding_function = OpenAIEmbeddings()
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

retriever = CustomRetriever(embeddings=embedding_function, chroma=db)

def retrieval_QA(query):
    result = retriever.get_relevant_documents(query)
    return result

retrieval_QA_tool = Tool.from_function(
    name="retrieval_QA",
    description="Retrieve data from Chroma database. Useful for when you need to answer questions about stored documents.",
    func=retrieval_QA
)
