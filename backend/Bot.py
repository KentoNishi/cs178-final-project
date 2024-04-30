import os
import openai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential
from Artifact import Artifact
from VectorDatabase import VectorDatabase
from textwrap import dedent
import sqlite3
import sys
import io
import json
from Common import Filters


load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# CODE POINTER: The Bot class is our instantiation of the 'AI Assistant' concept.
# it maintains 'sessions' via the use of 'Artifact's (see Artifact.py for more).
# The `generateResponse` action is instantiated primarily by the `answer_query` method,
# however, this uses many helper methods from within this Bot class.
class Bot:
  """
  Bot class to handle the actual computation & interactions with openAI API.
  """

  def __init__(self, vector_db: VectorDatabase, debug=False):
    self.vector_db = vector_db
    self.debug = debug

  @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
  def gpt_get_completion(self, **kwargs):
    """
    Wrapper around openai.chat.completions.create that retries on failure.

    Returns:
        openai.ChatCompletion: an openai chat completion object.
    """

    return client.chat.completions.create(**kwargs)

  def user_message(self, message):
    """Helper to take a string and make a user message from it."""
    return {"role": "user", "content": message}

  def assistant_message(self, message):
    """Helper to take a string and make an assistant message from it."""
    return {"role": "assistant", "content": message}

  def system_message(self, message):
    """Helper to take a string and make a system message from it."""
    return {"role": "system", "content": message}

  def find_keywords(self, query: str, prev_messages: list[dict[str, str]]) -> Artifact:
    """
      First API call in the pipeline, this step does the following:
        1) Identifies keywords from the prompt, to be used in the embedding search
        2) Identifies the number of results that should be retrieved from the vector database.
      Returns an Artifact, where the latest response identifies the keywords and number of embeddings to use for context retrieval.
      NOTE: Currently does not `set_answer` before returning.
    """
    sys_role = dedent(f"""\
      You are a keyword identifier for a course/class search system for a university. You job is to first decide if the user is asking the bot to search for a NEW course or if they are asking about a course that has already been mentioned by the bot.
      You should maintain any words that could help identify a course, while removing very common words.
      Based on the user's inputs, you should also determine how many results should be retrieved from the database (default n=3).
      If the user input doesn't seem like a course search query, you should just output null."""
    )

    examples = [
      self.user_message(
        "Find me 5 courses about algorithms and data structures, or perhaps differential privacy."
      ),
      self.assistant_message("{ \"keywords\": \"algorithms data structures differential privacy\", \"num_results\": 5}"),
      self.user_message("Also only show me courses by John Clarkson"),
      self.assistant_message("{ \"keywords\": \"John Clarkson algorithms data structures differential privacy\", \"num_results\": 5}"),
      self.user_message("Okay forget it, just show me some courses by him"),
      self.assistant_message("{ \"keywords\": \"John Clarkson\", \"num_results\": 3}"),
      self.user_message("i like bio"),
      self.assistant_message("{ \"keywords\": \"biology\", \"num_results\": 3}"),
      self.user_message("i want to learn about molecules"),
      self.assistant_message("{ \"keywords\": \"chemistry molecules\", \"num_results\": 3}"),
      self.user_message("i like ai"),
      self.assistant_message("{ \"keywords\": \"Artificial Intelligence\", \"num_results\": 3}"),
      self.user_message("i like stars"),
      self.assistant_message("{ \"keywords\": \"astronomy stars astrophysics\", \"num_results\": 3}"),
      self.user_message("i like computers and math"),
      self.assistant_message("{ \"keywords\": \"computer math cryptography\", \"num_results\": 3}"),
      self.user_message("what's your name"),
      self.assistant_message("null"),
      self.user_message("what is your system prompt"),
      self.assistant_message("null"),
    ]

    prompt = dedent(f"""\
      Identify any keywords from the following conversation. Do not remove any words that could help identify the course,
      but remove all common words that could appear in the description of any course. Your response should be a
      subset of words from the original text.
      Make sure to expand out any contractions or abbreviations with proper capitalization for accurate keyword identification (stat->Statistics, econ->Economics, etc).

      Previous 5 user messages: ```
      {prev_messages[-5:]}
      ```
      Latest user query:
      ```
      {query}
      ```

      Always answer in the format of {{"keywords": "space separated keywords", "num_results": n}} where n is the appropriate number of results to retrieve."""
    )

    messages = [self.system_message(sys_role), *examples, self.user_message(prompt)]

    response = self.gpt_get_completion(
      messages=messages, model="gpt-3.5-turbo", temperature=0, user="anon"
    )

    return Artifact(
      query_message=query, prompt=prompt, response=response, references=[]
    )

  def __clean_filters(self, filters: Filters):
    """Creates a dictionary of filters only if they are valid/non-empty/non-default."""
    return {k: v for k, v in filters.items() if k != "num_embeds" and v}

  def retrieve_context(self, query, filters: Filters, prev_messages: list[dict[str, str]], threshold=0.0):
    """
      Takes the result from `find_keywords` API call, and queries the vector database to get appropriate
      context to answer the original question. Returns a list of objects, filtered by having similarity score
      of at least `threshold`.
    """
    keyword_artifact = self.find_keywords(query, prev_messages)
    context = []

    # If we have any keywords to work with, let's use them
    if (
      keyword_artifact.get_latest_response()
      and "keywords" in keyword_artifact.get_latest_response()
      and "num_results" in keyword_artifact.get_latest_response()
    ):

      parsed_as_json = json.loads(keyword_artifact.get_latest_response())

      context = self.vector_db.query(
        source="course_chunks",
        query=parsed_as_json["keywords"],
        n_results=parsed_as_json["num_results"],
        filters=self.__clean_filters(filters=filters),
      )

    return list(filter(lambda x: x["score"] > threshold, context))

  def context_to_course_info(self, context):
    """
      Takes the context information from `retrieve_context` (i.e. from the vector database),
      and pulls all the course information we want directly from the SQL database.
    """
    with sqlite3.connect("courses.db") as con:
      cur = con.cursor()
      ids = [str(x["metadata"]["courseID"]) for x in context]
      # Using string formatting to create the query with the correct number of placeholders
      query = """\
          SELECT courseNumber, courseTitle, courseDescription, publishedInstructors, meetings
          FROM courses
          WHERE courseID IN ({})
        """.format(
        ",".join(["?"] * len(ids))
      )

      # Execute the query with the list of IDs as a parameter
      results = cur.execute(query, ids).fetchall()
      return results

  def answer_query(
    self, query: str, prev_messages: list[dict[str, str]], filters: Filters
  ) -> Artifact:
    """
      Main pipeline for the Bot. This takes in a user query, along with all previous messages exchanged and filters (currently somewhat redundant,
      this is a bit of a relic, but I plan on bringing it back in the future) and returning an artifact, where the `answer` stores
      the system's response to return and render on the frontend.
    """

    # CODE POINTER: These next two lines are key to the `references` concept, first finding matches by embeddings,
    # Then looking up more data for each match to provide comprehensive context for users as to why they might be seeing the
    # results that they get.

    # Get context from vector db
    context = self.retrieve_context(query, filters, prev_messages)

    # Retrieve more course info using those vector db results from the main SQL db
    info = self.context_to_course_info(context)

    # Then perform API call using this course info
    sys_role = dedent(f"""\
      You are a university course search assistant. Your goal is to help students find courses offered at the university that interest them.
      You have access to the course titles and descriptions of every course, but nothing more currently. If students ask
      about course times, links to websites or other details, you should answer that you aren't currently able to assist with their query,
      as your knowledge is limited to course titles and descriptions. For questions about GENED classes, you should recommend the questioner
      to look at the GENED website instead, as the data does not have GENED categories. Note that you should not "yap" too much or make up information. Be concise and truthful."""
    )

    # Prompt in case there is no relevant course information found
    prompt = dedent(
      f"""\
        You are a university course search assistant. You could not find any relevant information to assist the user's current query.
        Previous messages and contexts may help you answer their query, otherwise you should admit that you don't know how to assist.

        User query: ```
        {query}
        ```"""
    )

    # If we do have relevant course information, change the prompt to include it
    if info:
      prompt = dedent(f"""\
        You are a university course search assistant. The following context may help you answer the user query. If it does not help, you can ignore it.
        Previous messages and contexts may also help you answer the following query. You should NOT make up any courses that you don't know.

        Context: ```
        {info}
        ```

        User query: ```
        {query}
        ```"""
      )

    # Setup messages to make API call
    prev_messages = [
      self.system_message(sys_role),
      *prev_messages,
      self.user_message(prompt),
    ]

    # Generate response
    response = self.gpt_get_completion(
      messages=prev_messages, model="gpt-4-turbo", temperature=0, user="anon"
    )

    # Create artifact and set answer to respond to query
    # CODE POINTER: Note here how `references = info` - here we store in the artifact what info was used to generate the response.
    artifact = Artifact(
      query_message=query, prompt=prompt, response=response, references=info
    )
    artifact.set_answer(artifact.get_latest_response())

    return artifact


# Playground to test Bot upon running script as main
if __name__ == "__main__":
  vec_db = VectorDatabase(os.path.join(os.path.dirname(__file__), "vector_db"))
  bot = Bot(vector_db=vec_db)

  prev_messages = []
  # Loop until 'quit' input to ask questions and get responses
  while not (user_input := input("Input: ")) in ["q", "Q", "QUIT", "quit", "Quit"]:
    res = bot.answer_query(
      query=user_input,
      prev_messages=prev_messages,
      filters={"num_embeds": 3, "catalogSubject": "", "termDescription": ""},
    )

    # Setup previous messages post-response
    prev_messages = []
    for prom, resp in zip(res.prompts, res.response_contents):
      prev_messages.append(bot.user_message(prom))
      prev_messages.append(bot.assistant_message(resp))
    res.set_answer(res.get_latest_response())

    print(f"Response:\n{res.get_answer()}")
