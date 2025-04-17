import qrcode
import sqlite3
from flask import Flask, request, jsonify, render_template, send_file
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from datetime import datetime
from io import BytesIO

app = Flask(__name__, template_folder="templates")

GOOGLE_CLIENT_ID = "187158612965-272dhjdv16323lfsqo7osi17dqhsc8sd.apps.googleusercontent.com"

# ✅ Initialize Databases
def init_databases():
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE)''')
    
    # ✅ Sample Student Data (Only add if database is empty)
    students = [
        ("23BCY10304", "bcy10304@vitbhopal.ac.in"),
        ("23BCY10456", "bcy10456@vitbhopal.ac.in"),
        ("23BCY10578", "bcy10578@vitbhopal.ac.in"),
        ("23BCY10690", "bcy10690@vitbhopal.ac.in"),
        ("23BCY10832", "bcy10832@vitbhopal.ac.in"),
    ]
    c.executemany("INSERT OR IGNORE INTO students (student_id, email) VALUES (?, ?)", students)
    conn.commit()
    conn.close()

    # ✅ Create Attendance Table
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_email TEXT,
                    timestamp TEXT)''')
    conn.commit()
    conn.close()

init_databases()

@app.route("/")
def home():
    return render_template("home.html")

# ✅ Authenticate Google Sign-In
@app.route("/auth", methods=["POST"])
def auth():
    try:
        token = request.json.get("token")
        if not token:
            return jsonify({"success": False, "message": "No token provided"}), 400

        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        user_email = idinfo.get("email")

        # Verify student exists
        conn = sqlite3.connect("students.db")
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE email=?", (user_email,))
        student = c.fetchone()
        conn.close()

        if not student:
            return jsonify({"success": False, "message": "Unauthorized Student"}), 403

        # ✅ Mark Attendance
        conn = sqlite3.connect("attendance.db")
        c = conn.cursor()
        c.execute("INSERT INTO attendance (student_email, timestamp) VALUES (?, ?)", 
                  (user_email, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "email": user_email})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    
# ✅ Check if Student Exists & Has Already Marked Attendance
@app.route("/check_student", methods=["POST"])
def check_student():
    data = request.json
    student_email = data.get("email")
    slot = data.get("slot")


    # ✅ Check if student exists in students.db
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE email=?", (student_email,))
    student = c.fetchone()
    conn.close()

    if not student:
        return jsonify({"success": False, "message": "Email not found. Unauthorized access!"}), 403

    # ✅ Check if attendance is already marked for this slot
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("SELECT * FROM attendance WHERE student_email=? AND slot=?", (student_email, slot))
    existing_entry = c.fetchone()

    if existing_entry:
        conn.close()
        return jsonify({"success": False, "message": "Attendance already marked for this slot!"}), 403

    # ✅ Mark Attendance
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO attendance (student_email, slot, timestamp) VALUES (?, ?, ?)",
              (student_email, slot, timestamp))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Attendance marked successfully!"})

@app.route("/login")
def login():
    slot = request.args.get("slot")
    return render_template("login.html", slot=slot)  # Pass slot to template if needed

# ✅ Generate QR Code Based on Slot
@app.route("/generate_qr", methods=["GET"])
def generate_qr():
    slot = request.args.get("slot")

    if not slot:
        return jsonify({"success": False, "message": "No slot provided"}), 400

    # Corrected URL format
    qr_data = f"http://192.168.198.28:5000/login?slot={slot}"  # ✅ Now correctly points to the login route

    qr = qrcode.make(qr_data)
    img_io = BytesIO()
    qr.save(img_io, format="PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")

# ✅ Render Student Database Page
@app.route("/students")
def students():
    return render_template("students.html")

# ✅ Get Student List (For Student Page)
@app.route("/get_students", methods=["GET"])
def get_students():
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("SELECT email FROM students")
    students = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify({"students": students})



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)