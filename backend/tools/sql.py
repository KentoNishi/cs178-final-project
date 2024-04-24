import sqlite3
from langchain.tools import Tool

conn = sqlite3.connect("courses.db")


def run_sqlite_query(query):
    c = conn.cursor()
    c.execute(query)
    return c.fetchall()


run_query_tool = Tool.from_function(
    name="run_sqlite_query",
    description="""
    Run a sqlite query. The table name is courses with the following columns: 
    (courseID TEXT, termDescription TEXT, sessionDescription TEXT, catalogSchoolDescription TEXT, catalogSubject TEXT, catalogSubjectDescription TEXT, courseDescription TEXT, courseNumber TEXT, courseTitle TEXT, courseNotes TEXT, classLevelAttributeDescription TEXT, classCapacity INTEGER, subjectDescription TEXT, divisionalDistribution TEXT, quantitativeReasoning TEXT, courseComponent TEXT, gradingBasisDescription TEXT, publishedInstructors TEXT, meetings TEXT).
    """,
    func=run_sqlite_query
)