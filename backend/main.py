from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import asyncio
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
from typing import Dict, List, Any
from queue import Queue
from threading import Thread
from fastapi.middleware.cors import CORSMiddleware


class CallbackHandler(BaseCallbackHandler):
    """Callback handler class to give Kento the hooks he wants."""
    def __init__(self, queue) -> None:
        super().__init__()
        self._queue = queue
        # defining the stop signal that needs to be added to the queue in
        # case of the last token
        self._stop_signal = None

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Fires on LLM generating a new output token"""
        self._queue.put(token)

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Fires when LLM starts running."""
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Fires when LLM finishes generating response"""
        self._queue.put(self._stop_signal)

# Initialize callback handler
message_queue = Queue()
handler = CallbackHandler(message_queue)

app = FastAPI()

# TODO: Handle this a little better. This is just to fight CORS issues for the demo when running
# The backend on localhost
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# load OPENAI_API_KEY
load_dotenv()

# Define a Pydantic model for incoming data (do we actually need this?)
class Query(BaseModel):
    question: str

# Initialize necessary components
embedding_function = OpenAIEmbeddings()
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
retriever = db.as_retriever()
template = """Answer the question based only on the following context: {context} Question: {question} """
prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI(verbose=True, streaming=True, callbacks=[handler])
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
    """Non-streaming version"""
    try:
        print(query.question)
        result = chain.invoke(query.question)
        return {"recommendation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def response_generator(query):

    print(query)
    # Start a thread that runs the chain
    thread = Thread(target=chain.invoke, kwargs={"query": query})
    thread.start()

    # Main thread keeps pulling messages from the queue and yielding them
    while True:
        value = message_queue.get()
        if value == None:

            # End of message queue
            thread.join()
            return
        yield value
        message_queue.task_done()
        await asyncio.sleep(0.1)


@app.post('/query-stream/')
async def stream(query: Query):
    return StreamingResponse(response_generator(query.question), media_type='text/event-stream', timeout=None)