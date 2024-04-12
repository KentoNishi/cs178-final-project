import json
import sqlite3

# Load JSON data from a file
with open('./2248.json', 'r') as file:
    data = json.load(file)

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('courses.db')
c = conn.cursor()

# Create a table in the database
c.execute('''
CREATE TABLE IF NOT EXISTS courses (
    courseID TEXT,
    courseOfferNumber INTEGER,
    classKey TEXT,
    classNumber INTEGER,
    term TEXT,
    termDescription TEXT,
    likelyOfferedTerm TEXT,
    sessionCode TEXT,
    sessionDescription TEXT,
    sectionNumber TEXT,
    classCatalogNumber TEXT,
    catalogSchool TEXT,
    catalogSchoolDescription TEXT,
    catalogSubject TEXT,
    catalogSubjectDescription TEXT,
    classStatus TEXT,
    courseDescription TEXT,
    courseNumber TEXT,
    courseTitle TEXT,
    courseWebsite TEXT,
    courseNotes TEXT,
    classLevelAttribute TEXT,
    classLevelAttributeDescription TEXT,
    classMinUnits INTEGER,
    classMaxUnits INTEGER,
    crossRegistrationEligibleAttribute TEXT,
    likelyOffered TEXT,
    startDate TEXT,
    endDate TEXT,
    classCapacity INTEGER,
    classAlias TEXT,
    subjectDescription TEXT,
    classNotes TEXT,
    divisionalDistribution TEXT,
    quantitativeReasoning TEXT,
    consent TEXT,
    dropConsent TEXT,
    courseComponent TEXT,
    coopLink TEXT,
    gradingBasis TEXT,
    gradingBasisDescription TEXT,
    publishedInstructors TEXT,
    meetings TEXT
)
''')

# Insert data into the table
for course in data['courses']:
    c.execute('''
    INSERT INTO courses (
        courseID, courseOfferNumber, classKey, classNumber, term, termDescription,
        likelyOfferedTerm, sessionCode, sessionDescription, sectionNumber, classCatalogNumber,
        catalogSchool, catalogSchoolDescription, catalogSubject, catalogSubjectDescription,
        classStatus, courseDescription, courseNumber, courseTitle, courseWebsite, courseNotes,
        classLevelAttribute, classLevelAttributeDescription, classMinUnits, classMaxUnits,
        crossRegistrationEligibleAttribute, likelyOffered, startDate, endDate, classCapacity,
        classAlias, subjectDescription, classNotes, divisionalDistribution, quantitativeReasoning,
        consent, dropConsent, courseComponent, coopLink, gradingBasis, gradingBasisDescription,
        publishedInstructors, meetings
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        course['courseID'], course['courseOfferNumber'], course['classKey'], course['classNumber'],
        course['term'], course['termDescription'], course['likelyOfferedTerm'], course['sessionCode'],
        course['sessionDescription'], course['sectionNumber'], course['classCatalogNumber'],
        course['catalogSchool'], course['catalogSchoolDescription'], course['catalogSubject'],
        course['catalogSubjectDescription'], course['classStatus'], course['courseDescription'],
        course['courseNumber'], course['courseTitle'], course['courseWebsite'], course['courseNotes'],
        course['classLevelAttribute'], course['classLevelAttributeDescription'], course['classMinUnits'],
        course['classMaxUnits'], course['crossRegistrationEligibleAttribute'], course['likelyOffered'],
        course['startDate'], course['endDate'], course['classCapacity'], course['classAlias'],
        course['subjectDescription'], course['classNotes'], course['divisionalDistribution'],
        course['quantitativeReasoning'], course['consent'], course['dropConsent'], course['courseComponent'],
        course['coopLink'], course['gradingBasis'], course['gradingBasisDescription'],
        json.dumps(course.get('publishedInstructors', [])), json.dumps(course.get('meetings', []))
    ))

# Commit changes and close the connection
conn.commit()
conn.close()

print("JSON data has been successfully loaded into the SQLite database.")
