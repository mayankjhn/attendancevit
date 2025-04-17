import sqlite3

def add_students():
    # Connect to the database
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    # List of students with their emails and student ids
    students = [
        ("23BCY10304", "akshaya.23bcy10304@vitbhopal.ac.in"),
        ("23BCY10456", "bcy10456@vitbhopal.ac.in"),
        ("23BCY10578", "bcy10578@vitbhopal.ac.in"),
        ("23BCY10690", "bcy10690@vitbhopal.ac.in"),
        ("23BCY10832", "bcy10832@vitbhopal.ac.in")
    ]

    # Insert student data into the students table
    c.executemany("INSERT OR IGNORE INTO students (student_id, email) VALUES (?, ?)", students)
    conn.commit()

    print("Students added successfully!")
    conn.close()

if __name__ == "__main__":
    add_students()