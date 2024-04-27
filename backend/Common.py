from typing_extensions import TypedDict
from pydantic import BaseModel

# NOTE: Need to update this and the typescript stuff to allow for more/different filters
Filters = TypedDict("Filters",
  {
    "num_embeds": int,
    "termDescription": str,
    "catalogSubject": str
  }
)

# This class is essentially an artifact but without the methods, to allow passing it between front and backend
class ArtifactContent(BaseModel):
  query_message     : str
  prompts           : list[str]
  response_objects  : list[str]
  response_contents : list[str]
  references        : list[list[str]]
  answer            : str

class ClientMessage(BaseModel):
  artifact : ArtifactContent
  filters  : Filters