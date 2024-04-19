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


load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Bot:
    """
    Bot class to handle the actual computation & interactions with openAI API.
    """

    def __init__(self, vector_db: VectorDatabase=None, debug=False):
        self.vector_db = vector_db
        self.debug = debug

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    def gpt_get_completion(self, **kwargs):
        """
        Wrapper around openai.Completion.create that retries on failure.

        Returns:
            openai.ChatCompletion: an openai chat completion object.
        """

        return client.chat.completions.create(**kwargs)

    def user_message(self, message):
        return {"role": "user", "content": message}

    def assistant_message(self, message):
        return {"role": "assistant", "content": message}

    def system_message(self, message):
        return {"role": "system", "content": message}


    def find_keywords(self, query: str):

        sys_role = dedent(f"""\
            You are a keyword identifier for a course/class search system for a university.
            You should maintain any words that could help identify a course, while removing very common words.
        """)

        examples = [
            self.user_message("Please tell me about any classes that discuss algorithms and data structures, or perhaps differential privacy."),
            self.assistant_message("algorithms data structures differential privacy"),
            self.user_message("Actually, I want a course taught by John Clarkson, preferably on Mondays."),
            self.assistant_message("John Clarkson Mondays"),
            self.user_message("Please tell me more about that"),
            self.assistant_message("")
        ]

        prompt = dedent(f"""\
            Identify any keywords from the following text. Do not remove any words that could help identify the course,
            but remove all common words that could appear in the description of any course. Your response should be a
            subset of words from the original text.

            ```
            {query}
            ```
        """)

        messages = [
            self.system_message(sys_role),
            *examples,
            self.user_message(prompt)
        ]

        response = self.gpt_get_completion(messages=messages, model="gpt-3.5-turbo", temperature=0, user="anon")

        return Artifact(query_message=query, prompt=prompt, response=response, references=[])

    def retrieve_context(self, query, n_results=3, threshold=0.6):
      keyword_artifact = self.find_keywords(query)
      context = []

      print(keyword_artifact.get_latest_response())

      # If we have any keywords to work with, let's use them
      if (keyword_artifact.get_latest_response()):

        # Temporary hack to redirect stdout and stderr for this operation to not have to deal with these add existing embedding id things
        temp_out = io.StringIO()
        old_out = sys.stdout
        old_err = sys.stderr
        sys.stdout = temp_out
        sys.stderr = temp_out

        context = self.vector_db.query(source="course_chunks", query=keyword_artifact.get_latest_response(), n_results=n_results, filters={})

        # Restore stdout/stderr to original values
        sys.stdout = old_out
        sys.stderr = old_err
        print(context)

      # print(keyword_artifact)
      # print(context)
      return list(filter(lambda x: x["score"] > threshold, context))

    def context_to_course_info(self, context):
      with sqlite3.connect("courses.db") as con:
        cur = con.cursor()
        ids = [x["id"] for x in context]

        # Using string formatting to create the query with the correct number of placeholders
        query = """
            SELECT courseNumber, courseTitle, courseDescription, publishedInstructors, meetings
            FROM courses
            WHERE courseID IN ({})
        """.format(','.join(['?']*len(ids)))

        # Execute the query with the list of IDs as a parameter
        results = cur.execute(query, ids).fetchall()
        return results


    def answer_query(self, messages: list[dict[str, str]]):
      query = messages.pop()["content"]

      context = self.retrieve_context(query)

      info = self.context_to_course_info(context)

      sys_role = dedent(f"""\
        You are a university course search assistant. Your goal is to help students find courses offered at the university that interest them.
        You have access to the course titles and descriptions of every course, but nothing more currently. If students ask
        about course times, links to websites or other details, you should answer that you aren't currently able to assist with their query,
        as your knowledge is limited to course titles and descriptions.
      """)

      prompt = dedent(f"""\
          You are a university course search assistant. You could not find any relevant information to assist the user's current query.
          Previous messages and contexts may help you answer their query, otherwise you should admit that you don't know how to assist.

          User query: ```
          {query}
          ```
        """)
      if context:
        prompt = dedent(f"""\
          You are a university course search assistant. The following context may help you answer the user query. If it does not help, you can ignore it.
          Previous messages and contexts may also help you answer the following query.

          Context: ```
          {info}
          ```

          User query: ```
          {query}
          ```
          """)


      messages = [
        self.system_message(sys_role),
        *messages,
        self.user_message(prompt)
      ]

      response = self.gpt_get_completion(messages=messages, model="gpt-4-turbo", temperature=0, user="anon")

      return Artifact(query_message=query, prompt=prompt, response=response, references=[])


vec_db = VectorDatabase(os.path.join(os.path.dirname(__file__), 'vector_db'))

bot = Bot(vector_db=vec_db)
res = bot.answer_query([
    {
      "role": "user",
      "content": "Please find me a course about data structures and algorithms"
    }
  ])
# print(res.get_latest_prompt())
# print(res.get_latest_response())