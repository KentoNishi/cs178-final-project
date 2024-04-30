from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from Bot import Bot
from Common import ArtifactContent, ClientMessage
from VectorDatabase import VectorDatabase
import os

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

class Server:
  def __init__(self, bot: Bot):
    self.bot = bot
    self.router = APIRouter()
    self.router.add_api_route("/recommend", self.recommend, methods=["POST"])

  def recommend(self, query : ClientMessage) -> ArtifactContent:

    artifact = query.artifact
    # Reconstruct messages from what was sent
    prev_messages = []
    for prompt, resp in zip(artifact.prompts, artifact.response_contents):
      prev_messages.append(bot.user_message(prompt))
      prev_messages.append(bot.assistant_message(resp))

    artifact = self.bot.answer_query(query=artifact.query_message, prev_messages=prev_messages, filters={
      "num_embeds": 3,
      "catalogSubject": "",
      "termDescription": ""
    })
    # Returning an ArtifactContent object (contains all of the content from Artifact, just no methods etc, don't want to send useless stuff)
    return artifact.to_artifact_content()

vec_db = VectorDatabase(db_path=os.path.join(os.path.dirname(__file__), "vector_db"))
bot = Bot(vector_db=vec_db)
server = Server(bot=bot)

app.include_router(server.router)