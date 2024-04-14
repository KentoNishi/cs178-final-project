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
EMBEDDING_FILE  = "../embeddings/embeddings.jsonl"
DATA = {
  "fall24": FALL_DATA,
  "spring25": SPRING_DATA
}


def get_embedding(text, model="text-embedding-3-small"):

  # Replace newline characters with spaces in the text
  text = text.replace("\n", " ")

  # Using only first embedding
  return client.embeddings.create(input=[text], model=model).data[0].embedding

# Creating embeddings for all input files
for (outname, input_file) in DATA.items():
  with open(input_file, "r") as f:
    processed = 0
    data = json.load(f)
    courses_in_file = len(data["courses"])

    # Will store all embeddings for every course!
    # Maps courseID to list of embeddings for that course, generated from
    # 1) courseTitle 2) chunks of courseDescription, each 500 chars.
    embeddings = defaultdict(list)

    for course in data["courses"]:
      soup = BeautifulSoup(course["courseDescription"], "html.parser")
      text = soup.get_text()

      # Split the text into chunks of 500 characters and store them in a list called 'chunks'
      chunks = [text[i:i+500] for i in range(0, len(text), 500)]

      # Create embeddings for all chunks of course description
      for chunk in chunks:
        embeddings[course["courseID"]].append({
          "embedding": get_embedding(chunk),
          "text": chunk
        })

      # Also create embedding for course title
      embeddings[course["courseID"]].append({
        "embedding": get_embedding(course["courseTitle"]),
        "text": course["courseTitle"]
      })
      processed += 1
      progbar(processed, courses_in_file, 20, False)
    print(f"Finished processing data file {input_file}")

    # Open a new file 'embeddings.jsonl' in write mode
    print("Writing embeddings to file...")
    with open(EMBEDDING_FILE, "w") as f:
      json.dump(embeddings, f)

    print("Embeddings written to file 'embeddings.jsonl'")