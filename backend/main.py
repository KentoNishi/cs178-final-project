from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv

app = FastAPI()

# load OPENAI_API_KEY
load_dotenv()

# Define a Pydantic model for incoming data
class Query(BaseModel):
    question: str

# Initialize necessary components
embedding_function = OpenAIEmbeddings()
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
retriever = db.as_retriever()
template = """Answer the question based only on the following context: {context} Question: {question} """
prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI(verbose=True)
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

@app.get("/")
async def root():
    return {"message": "API for my.harvard chatbot"}

@app.post("/recommend")
async def recommend_classes(query: Query):
    try:
        result = chain.invoke(query.question)
        return {"recommendation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Create and populate Chroma database and Save to disk
# print("created chroma db")
# loader = JSONLoader(file_path="./2248.json", jq_schema=".courses[]", text_content=False)
# documents = loader.load()
# db = Chroma.from_documents(documents, embedding_function, persist_directory="./chroma_db",)