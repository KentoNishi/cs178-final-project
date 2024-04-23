import json
from openai import OpenAI
import sys
import os
from bs4 import BeautifulSoup
from collections import defaultdict
from utils import progbar, load_env
from textwrap import dedent

# Load backend .env, needed for OpenAI API key.
# NOTE: Might need to remove in Docker environment, or might just be redundant.
load_env()

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

FALL_DATA   = "../data/2248.json"
SPRING_DATA = "../data/2252.json"
EMBEDDING_FILE  = "../embeddings/embeddings_new.jsonl"
DATA = {
  "fall24": FALL_DATA,
  "spring25": SPRING_DATA
}

LINEAR_EMBEDS = [
  "courseTitle",
  "courseNumber",
  "termDescription",
  "publishedInstructors",
  "meetings",
  "courseDescription"
]


def get_embedding(text, model="text-embedding-3-small"):

  # Replace newline characters with spaces in the text
  text = text.replace("\n", " ")

  # Using only first embedding
  return client.embeddings.create(input=[text], model=model).data[0].embedding


class Embedder():
  def __init__(self, input_data : dict[str, str], output_path : str, sample_output_path : str, client):
    self.input_data = input_data
    self.client = client
    self.output_path = output_path
    self.sample_output_path = sample_output_path

  def __embed_sample(self, course_embedder, version_num: str, **kwargs):
    """
      Creates a sample of the embedding system, with one example per input file.
      Embeds each course using `course_embedder`, and outputs a file named using `version_num`.
      `kwargs` must contain any attributes that the `course_embedder` needs, else will fail.
    """
    for (outname, input_file) in self.input_data.items():
      embeddings = defaultdict(list)
      with open(input_file, "r") as f:
        # All data from file
        data = json.load(f)

        # Only want one course as a sample
        course = data["courses"][0]

        course_embedder(course, embeddings, kwargs)

      with open(os.path.join(self.sample_output_path, f"{outname}_{version_num}_sample.jsonl"), "w") as outfile:
        json.dump(embeddings, outfile)

  def __embed_semester(self, course_embedder, semester: str, version_num: str, **kwargs):
    """
      Embeds a semester's worth of data (i.e. an entire input file),
      making a new `embeddings` variable and dumping it all to a json file
      with the name `{semester}_v1.json`.
    """
    embeddings = defaultdict(list)

    if not (semester in self.input_data):
      print("Invalid semester key in embed_semester_v1")
      return

    input_file = self.input_data[semester]
    with open(input_file, "r") as f:
      processed = 0
      data = json.load(f)
      courses_in_file = len(data["courses"])
      print(f"There are {courses_in_file} courses for {semester}.")

      for course in data["courses"]:
        course_embedder(course, embeddings, kwargs)
        processed += 1
        progbar(processed, courses_in_file, 20, False)

      print(f"Finished processing {semester} semester")

    # Open a new file 'embeddings.jsonl' in write mode
    output_path = os.path.join(self.output_path, f"{semester}_{version_num}.json")
    print("Writing embeddings to file...")
    with open(output_path, "w") as f:
      json.dump(embeddings, f)

    print(f"Embeddings written to file {output_path}")
    return

  def __embed_all(self, course_embedder, version_num: str, **kwargs):
    """
      Creates embeddings for all semesters in `input_data`.
      Calls `course_embedder` to embed each course via `embed_semester`.
    """
    for (semester) in self.input_data.keys():
      self.__embed_semester(course_embedder, semester, version_num, kwargs)

  def embed_course_v1(self, course, embeddings, kwargs) -> bool:
    """
      Embeds a course according to my v1 spec.
      For each course, creates an embedding for:
        - 500 char chunks of the courseDescription
        - Everything in `linear_attributes`
      and adds it to the dictionary `embeddings` in the list corresponding to the `courseID`.
    """

    if "linear_attributes" not in kwargs:
      print("Need to pass `linear_attributes` to `embed_course_v1`.")
      return False

    linear_attributes = kwargs['linear_attributes']

    soup = BeautifulSoup(course["courseDescription"], "html.parser")
    text = soup.get_text()

    # Split the text into chunks of 500 characters and store them in a list called 'chunks'
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]

    # Create embeddings for all chunks of course description
    for chunk in chunks:
      embeddings[course["courseID"]].append({
        "embedding": get_embedding(chunk),
        "text": chunk,
        "type": "descriptionChunk"
      })

    # Create embeddings for a number of other things that linearly map to a courseID
    for attribute in linear_attributes:
      try:
        if (course[attribute]):
          embeddings[course["courseID"]].append({
            "embeddings": get_embedding(str(course[attribute])),
            "text": course[attribute],
            "type": attribute
          })
      except Exception as e:
        print(f"Issue with courseID: {course['courseID']}, {course['courseTitle']}, attribute: {attribute}, value: {course[attribute]}")
        print(e)

    return True

  def embed_semester_v1(self, semester: str, linear_attributes):
    self.__embed_semester(self.embed_course_v1, semester, "v1", linear_attributes=linear_attributes)

  def embed_sample_v1(self, linear_attributes):
    self.__embed_sample(self.embed_course_v1, "v1", linear_attributes=linear_attributes)

  def embed_v1(self, linear_attributes):
    """
      Creates embeddings for all semesters in `input_data`.
      Calls `__embed_all` to embed each semester.
    """
    self.__embed_all(self.embed_course_v1, "v1", linear_attributes=linear_attributes)

  def embed_course_v2(self, course, embeddings, kwargs) -> bool:
    """
      Embeds a course according to my v1 spec.
      For each course, creates an embedding for:
        - 500 char chunks of the courseDescription
        - Everything in `linear_attributes`
      and adds it to the dictionary `embeddings` in the list corresponding to the `courseID`.
    """

    linear_tags = [
      "termDescription",
      "catalogSubjectDescription",
      "courseNumber",
      "courseTitle",
      "classLevelAttributeDescription",
      "divisionalDistribution"
    ]

    def create_chunks_v2(course, linear_tags):
      """
        Creates what I've called `enchancedDescriptionChunks` from a `courseDescription`.
        Again, split by 500 chars, but the enchaned chunk is that chunk, but with added
        info about the course.
         -> Everything in `linear_tags` is included after the chunk, comma separated.
         -> Then the name of the instructors are added on the next line.
         -> Finally, any meeting days are put on the final line.

        The aim is to tackle queries that provide info on multiple axes and provide better results,
        e.g. the query 'I want a Computer Science course that meets on Mondays', now
        `Computer Science` and `Monday` should both appear in the same chunk, hence the same embedding,
        and hopefully will more reliably find relevant courses.
      """
      soup = BeautifulSoup(course["courseDescription"], "html.parser")
      text = soup.get_text()

      chunks = [text[i:i + 500] for i in range(0, len(text), 500)]

      # some meetings are just like 'TBA' - this aims to ignore these, otherwise this keeps
      # all unique days the class meets upon (ignores times for now)
      chunks = list(map(
        lambda chunk: dedent(f"""\
          {chunk}

          {','.join([course[tag] if course[tag] else "" for tag in linear_tags])},
          {','.join(map(lambda instr: instr['instructorName'], course['publishedInstructors']))},
          {','.join(set().union(
            *map(lambda pattern: [] if isinstance(pattern, str) else pattern['daysOfWeek'], course['meetings'])
            ))}
          """),
        chunks
      ))
      return chunks

    chunks = create_chunks_v2(course, linear_tags=linear_tags)

    # Create embeddings for all (enhanced) chunks
    for chunk in chunks:
      embeddings[course["courseID"]].append({
        "embedding": get_embedding(chunk),
        "text": chunk,
        "type": "enhancedDescriptionChunk"
      })

    return True

  def embed_sample_v2(self):
    self.__embed_sample(self.embed_course_v2, "v2")

  def embed_semester_v2(self):
    self.__embed_semester(self.embed_course_v2, "spring25", "v2")

embedder = Embedder(
  input_data=DATA,
  output_path=os.path.join(os.path.dirname(__file__), "..", "embeddings"),
  sample_output_path=os.path.join(os.path.dirname(__file__), "..", "embeddings", "samples"),
  client=client
)

embedder.embed_semester_v2()