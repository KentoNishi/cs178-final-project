import sqlite3
from langchain.tools import Tool

conn = sqlite3.connect("courses.db")


def run_sqlite_query(query):
    c = conn.cursor()
    c.execute(query)
    return c.fetchall()


run_query_tool = Tool.from_function(
    name="run_sqlite_query",
    description="Run a sqlite query. The table name is courses with the following columns (courseID TEXT, courseOfferNumber INTEGER, classKey TEXT, classNumber INTEGER, term TEXT, termDescription TEXT, likelyOfferedTerm TEXT, sessionCode TEXT, sessionDescription TEXT, sectionNumber TEXT, classCatalogNumber TEXT, catalogSchool TEXT, catalogSchoolDescription TEXT, catalogSubject TEXT, catalogSubjectDescription TEXT, classStatus TEXT, courseDescription TEXT, courseNumber TEXT, courseTitle TEXT, courseWebsite TEXT, courseNotes TEXT, classLevelAttribute TEXT, classLevelAttributeDescription TEXT, classMinUnits INTEGER, classMaxUnits INTEGER, crossRegistrationEligibleAttribute TEXT, likelyOffered TEXT, startDate TEXT, endDate TEXT, classCapacity INTEGER, classAlias TEXT, subjectDescription TEXT, classNotes TEXT, divisionalDistribution TEXT, quantitativeReasoning TEXT, consent TEXT, dropConsent TEXT, courseComponent TEXT, coopLink TEXT, gradingBasis TEXT, gradingBasisDescription TEXT, publishedInstructors TEXT, meetings TEXT).",
    func=run_sqlite_query
)
