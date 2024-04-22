"""
Generates JSON lines document of the form:

{courseID:
  [
    {
      embedding: [....],
      text: "...."
    },
    {
      embedding: [....],
      text: "...."
    }
  ]
}
{
  ...
}
"""

import json
from openai import OpenAI
import sys
import os
from bs4 import BeautifulSoup
from collections import defaultdict
from utils import progbar, load_env

# Load backend .env, needed for OpenAI API key
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

  def embed_course_v1(self, course, embeddings, linear_attributes):
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

    return


  def embed_v1_sample(self, linear_attributes):
    """
      Creates a sample of the embedding system, with one example per input file.
    """

    for (outname, input_file) in self.input_data.items():
      embeddings = defaultdict(list)
      with open(input_file, "r") as f:
        # All data from file
        data = json.load(f)

        # Only want one course as a sample
        course = data["courses"][0]

        self.embed_course_v1(course, embeddings, linear_attributes)

      with open(os.path.join(self.sample_output_path, f"{outname}_v1_sample.json"), "w") as outfile:
        json.dump(embeddings, outfile)

  def embed_v1_semester(self, linear_attributes, semester: str):
    embeddings = defaultdict(list)

    if not (semester in self.input_data):
      print("Invalid semester key in embed_v1_semester")
      return

    input_file = self.input_data[semester]
    with open(input_file, "r") as f:
      processed = 0
      data = json.load(f)
      courses_in_file = len(data["courses"])
      print("There are {courses_in_file} courses for {semester}.")

      for course in data["courses"]:
        self.embed_course_v1(course, embeddings, linear_attributes)
        processed += 1
        progbar(processed, courses_in_file, 20, False)

      print(f"Finished processing {semester} semester")

    # Open a new file 'embeddings.jsonl' in write mode
    output_path = os.path.join(self.output_path, f"{semester}_v1.json")
    print("Writing embeddings to file...")
    with open(output_path, "w") as f:
      json.dump(embeddings, f)

    print("Embeddings written to file {output_path}")
    return


  def embed_v1(self, linear_attributes):
    """
      Simple embedding system:


    """
    # Will store all embeddings for every course!
    # Maps courseID to list of embeddings for that course, generated from
    # 1) courseTitle 2) chunks of courseDescription, each 500 chars.
    embeddings = defaultdict(list)

    # Creating embeddings for all input files
    for (outname, input_file) in self.input_data.items():
      with open(input_file, "r") as f:
        processed = 0
        data = json.load(f)
        courses_in_file = len(data["courses"])


        for course in data["courses"]:
          self.embed_course_v1(course, embeddings, linear_attributes)
          processed += 1
          progbar(processed, courses_in_file, 20, False)

        print(f"Finished processing data file {input_file}")

      # Open a new file 'embeddings.jsonl' in write mode
      print("Writing embeddings to file...")
      with open(EMBEDDING_FILE, "w") as f:
        json.dump(embeddings, f)

      print("Embeddings written to file 'embeddings.jsonl'")

embedder = Embedder(
  input_data=DATA,
  output_path=os.path.join(os.path.dirname(__file__), "..", "embeddings"),
  sample_output_path=os.path.join(os.path.dirname(__file__), "..", "embeddings", "samples"),
  client=client
)

embedder.embed_v1_semester(linear_attributes=LINEAR_EMBEDS, semester="spring25")