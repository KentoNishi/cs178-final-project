from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import asyncio
from typing import Dict, List, Any
from queue import Queue
from threading import Thread
from fastapi.middleware.cors import CORSMiddleware
from Bot import Bot
from VectorDatabase import VectorDatabase
import os
from Artifact import Artifact

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

# This class is essentially an artifact but without the methods, to allow passing it between front and backend
class ArtifactContent(BaseModel):
  query_message     : str
  prompts           : list[str]
  response_objects  : list[str]
  response_contents : list[str]
  references        : list[list[str]]
  answer            : str

# class Query(BaseModel):
#   artifact : Artifact

class Server:
  def __init__(self, bot: Bot):
    self.bot = bot
    self.router = APIRouter()
    self.router.add_api_route("/recommend", self.recommend, methods=["POST"])

  def recommend(self, query : ArtifactContent):

    # Reconstruct messages from what's was sent
    prev_messages = []
    for prompt, resp in zip(query.prompts, query.response_contents):
      prev_messages.append(bot.user_message(prompt))
      prev_messages.append(bot.assistant_message(resp))

    # if not query.artifact.query_message:
    #   return { "status": "ERR: No query message" }

    return self.bot.answer_query(query=query.query_message, prev_messages=prev_messages)


vec_db = VectorDatabase(db_path=os.path.join(os.path.dirname(__file__), "vector_db"))
bot = Bot(vector_db=vec_db)
server = Server(bot=bot)

app.include_router(server.router)