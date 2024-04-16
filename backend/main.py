from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_community.document_loaders import JSONLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv

# load OPENAI_API_KEY
load_dotenv()

embedding_function = OpenAIEmbeddings()

# Create and populate Chroma database and Save to disk
# print("created chroma db")
# loader = JSONLoader(file_path="./2248.json", jq_schema=".courses[]", text_content=False)
# documents = loader.load()
# db = Chroma.from_documents(documents, embedding_function, persist_directory="./chroma_db",)

# load from disk
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)


retriever = db.as_retriever()

template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI(verbose=True)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

query = "recommend me a couple of computer science class that meets on mondays and wednesdays"
print(chain.invoke(query))
