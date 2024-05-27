import sqlite3
import random

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS enrollments (
        student_id INTEGER,
        course_id INTEGER,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(course_id) REFERENCES courses(id)
    )
''')

# Predefined list of courses
courses = ['Math', 'Physics', 'Biology', 'Philosophy', 'English']

# Insert courses into the courses table
for course in courses:
    cursor.execute('INSERT INTO courses (name) VALUES (?)', (course,))

# Sample student names
student_names = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']

# Insert students and randomly enroll them in courses
for name in student_names:
    cursor.execute('INSERT INTO students (name) VALUES (?)', (name,))
    student_id = cursor.lastrowid
    enrolled_courses = random.sample(range(1, len(courses)+1), random.randint(1, 2))
    for course_id in enrolled_courses:
        cursor.execute('INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)', (student_id, course_id))

# Commit the transactions
conn.commit()

# Verify the content of the tables
print("Students:")
for row in cursor.execute('SELECT * FROM students'):
    print(row)

print("\nCourses:")
for row in cursor.execute('SELECT * FROM courses'):
    print(row)

print("\nEnrollments:")
for row in cursor.execute('SELECT * FROM enrollments'):
    print(row)

# Close the connection
conn.close()