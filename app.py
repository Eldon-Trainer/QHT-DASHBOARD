from flask import Flask, request, jsonify
import csv, hashlib
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Allows frontend (HTML) to communicate with backend

USER_FILE = os.path.join(os.path.dirname(__file__), "user.csv")
DEFAULT_PASSWORD = "qht@123"

# --- Utility functions ---
def hash_password(password):
    return hashlib.sha1(password.encode()).hexdigest()

def load_users():
    users = {}
    with open(USER_FILE, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            users[row["username"]] = {
                "password_hash": row["password_hash"],
                "role": row["role"],
                "department": row["department"]
            }
    return users

def save_users(users):
    with open(USER_FILE, "w", newline="") as csvfile:
        fieldnames = ["username", "password_hash", "role", "department"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user, data in users.items():
            writer.writerow({
                "username": user,
                "password_hash": data["password_hash"],
                "role": data["role"],
                "department": data["department"]
            })

# --- Routes ---
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_users()
    if username not in users:
        return jsonify({"success": False, "message": "User not found"}), 404

    if hash_password(password) == users[username]["password_hash"]:
        first_login = password == DEFAULT_PASSWORD
        return jsonify({
            "success": True,
            "message": "Login successful",
            "role": users[username]["role"],
            "department": users[username]["department"],
            "first_login": first_login
        })
    else:
        return jsonify({"success": False, "message": "Incorrect password"}), 401

@app.route("/reset_password", methods=["POST"])
def reset_password():
    data = request.json
    username = data.get("username")
    new_password = data.get("new_password")

    users = load_users()
    if username not in users:
        return jsonify({"success": False, "message": "User not found"}), 404

    users[username]["password_hash"] = hash_password(new_password)
    save_users(users)
    return jsonify({"success": True, "message": "Password updated successfully"})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
