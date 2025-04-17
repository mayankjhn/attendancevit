import sqlite3

conn = sqlite3.connect("attendance.db")
c = conn.cursor()

# ✅ Modify Attendance Table to Store Slot
c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_email TEXT,
                slot TEXT,
                timestamp TEXT,
                UNIQUE(student_email, slot))''')  # Prevent duplicate entries

conn.commit()
conn.close()