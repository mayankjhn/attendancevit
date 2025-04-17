from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # ✅ Allow frontend to communicate with backend

@app.route('/check_student', methods=['POST'])
def check_student():
    data = request.json
    email = data.get("email")   
    passkey = data.get("passkey")

    if not email or not passkey:
        return jsonify({"success": False, "message": "Missing email or passkey"}), 400

    if passkey == "123456":  # ✅ Your expected passkey
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid passkey"}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # ✅ Runs on PORT 5000