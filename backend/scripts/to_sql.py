import sqlite3
import json
import os
import sys
from config import CONFIG

# Function to convert Python object to JSON-formatted string if not None
def json_dumps_or_none(obj):
    return json.dumps(obj) if obj is not None else None

# File path to your JSON data
# json_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "2252.json")

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "..", "courses.db"))
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS courses (
    courseID TEXT,
    termDescription TEXT,
    sessionDescription TEXT,
    catalogSchoolDescription TEXT,
    catalogSubject TEXT,
    catalogSubjectDescription TEXT,
    courseDescription TEXT,
    courseNumber TEXT,
    courseTitle TEXT,
    courseNotes TEXT,
    classLevelAttributeDescription TEXT,
    classCapacity INTEGER,
    subjectDescription TEXT,
    divisionalDistribution TEXT,
    quantitativeReasoning TEXT,
    courseComponent TEXT,
    gradingBasisDescription TEXT,
    publishedInstructors TEXT,
    meetings TEXT
)
''')

# Function to convert list of dictionaries to a JSON array of names
def json_instructor_names(instructors):
    return json.dumps([instructor['instructorName'] for instructor in instructors]) if instructors else json.dumps([])


for input_file in CONFIG.raw_input_files:
  # Read JSON data from file
  with open(input_file, 'r') as file:
    data = json.load(file)

    # Insert data into the table
    for course in data['courses']:
      cursor.execute('''
      INSERT INTO courses (
          courseID, termDescription, sessionDescription, catalogSchoolDescription, catalogSubject,
          catalogSubjectDescription, courseDescription, courseNumber, courseTitle, courseNotes,
          classLevelAttributeDescription, classCapacity, subjectDescription, divisionalDistribution,
          quantitativeReasoning, courseComponent, gradingBasisDescription, publishedInstructors, meetings
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''', (
          course['courseID'],
          course['termDescription'],
          course['sessionDescription'],
          course['catalogSchoolDescription'],
          course['catalogSubject'],
          course['catalogSubjectDescription'],
          course['courseDescription'],
          course['courseNumber'],
          course['courseTitle'],
          course['courseNotes'],
          course['classLevelAttributeDescription'],
          course['classCapacity'],
          course['subjectDescription'],
          course['divisionalDistribution'],
          json_dumps_or_none(course.get('quantitativeReasoning')),
          course['courseComponent'],
          course['gradingBasisDescription'],
          json_instructor_names(course.get('publishedInstructors')),
          json.dumps(course.get('meetings'))
      ))

    # Commit change
    conn.commit()

# close connection
conn.close()