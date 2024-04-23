from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.prompts import ChatPromptTemplate
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.schema import SystemMessage
from langchain_openai import ChatOpenAI
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import asyncio
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
from typing import Dict, List, Any
from queue import Queue
from threading import Thread
from fastapi.middleware.cors import CORSMiddleware
from tools.sql import run_query_tool
from tools.retrieve import retrieval_QA_tool
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory

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


tools = [run_query_tool, retrieval_QA_tool]


prompt = ChatPromptTemplate(
    messages=[
        SystemMessage(content=("""
                               You are a chatbot trained to assist with Harvard college course recommendations. 
                               Please provide detailed, accurate, and concise responses to the questions asked, 
                               utilizing the following tools when necessary: {tools}.
                               For example, when question about metadata is asked, use run_query_tool first. 
                               When asked about more content realated things, use retrieval_QA_tool.
                               """
        )),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=4)

model = ChatOpenAI(verbose=True, callbacks=[handler])

agent = OpenAIFunctionsAgent(
    llm=model,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(
    agent=agent,
    verbose=True,
    tools=tools,
    memory=memory
)


@app.get("/")
async def root():
    return {"message": "API for my.harvard chatbot"}

@app.post("/recommend")
async def recommend_classes(query: Query):
    """Non-streaming version"""
    try:
        print(query.question)
        result = agent_executor(query.question)
        return {"recommendation": result['output']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# async def response_generator(query):

#     print(query)
#     # Start a thread that runs the chain
#     thread = Thread(target=chain.invoke, kwargs={"query": query})
#     thread.start()

#     # Main thread keeps pulling messages from the queue and yielding them
#     while True:
#         value = message_queue.get()
#         if value == None:

#             # End of message queue
#             thread.join()
#             return
#         yield value
#         message_queue.task_done()
#         await asyncio.sleep(0.1)


# @app.post('/query-stream/')
# async def stream(query: Query):
#     return StreamingResponse(response_generator(query.question), media_type='text/event-stream', timeout=None)