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
from Common import ClientMessage

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

with open("../extension/src/assets/welcome.md") as f:
    welcome_message = f.read()

system_prompt = ("""You are an LLM agent assiting students in searching courses on my.harvard (the system Harvard students use for finding courses).
You will be provided a sequence of chat messages you and the user have exchanged in the chat assistant panel.
Please provide detailed, accurate, and concise responses to the questions asked, utilizing the following tools when necessary:
{tools}

run_query_tool should be used to search for courses in the database. retrieval_QA_tool uses vector similarity, so it might not always return the most accurate results.
You can use the tools in any order and as many times as you need to answer the user's question.
It is recommended to execute queries using run_query_tool first, and only resort to retrieval_QA_tool if you are unable to find something.
When using run_query_tool, use SQL's OR functionality to also match expanded abbreviations. Also consider using non-case-sensitive and non-space-sensitive queries to maximize the chances of finding good results.

If you are unsure about the answer, you can ask the user for more information.
Additionally, you only have access to the database of courses for the FALL 2024 semester.
If you suspect that the user is asking about something that is not in the database, you can communicate that to the user.
If you are unable to find the answer to a question, clarify what information you looked for and what you were unable to find.

Some additional context which may be useful as a Harvard-specific chatbot:
- A "gem" is a course that is considered to be particularly low-stress and enjoyable. You cannot judge gem courses, so explain this to the user if asked.
- A "concentration" is a major.
- A PF is a pass/fail course.
- A "GENED" is a general education requirement.
- Harvard students use abbreviations for courses like CS or COMPSCI (Computer Science), AM (Applied Math), EC (Economics), etc.
- If a course search does not yield any results, try again with slightly different phrasing, abbreviations, or wording.
- If a course search seems to yield inaccurate results, try again but expand out abbreviations or use more general terms at your discretion.

IMPORTANT:
DO NOT EVER output information about a course which is false or misleading.
Before mentioning a course, check that it actually exists with an extra query in the database.
At the same time, if you can't find a relevant course, change your queries and keep trying. If you are still unable to find the course, communicate that to the user.
""")

prompt = ChatPromptTemplate(
    messages=[
        SystemMessage(content=system_prompt),
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
async def recommend_classes(query: ClientMessage):
    """Non-streaming version"""
    try:
        result = agent_executor(query.artifact.query_message)
        return {"recommendation": result['output']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset-agent")
async def reset_agent():
    agent_executor.memory.clear()
    return {"message": "Agent reset"}

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