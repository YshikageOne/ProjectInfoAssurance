from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_PATH
from jwt import encode
import datetime
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXP_DELTA_SECONDS

app = Flask(__name__)

def get_db_connection():
    return sqlite3.connect(DB_PATH)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        password_hash = generate_password_hash(password)
        cursor.execute("INSERT INTO Users (Username, PasswordHash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    print(f'🔍 Login attempt for "{username}"')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT PasswordHash FROM Users WHERE Username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        print(f'{request.remote_addr} - POST /login ❌ RESULT: Username not found.')
        return jsonify({'status': 'fail', 'message': 'Username not found.'}), 404

    stored_hash = result[0]

    if not check_password_hash(stored_hash, password):
        print(f'{request.remote_addr} - POST /login ❌ RESULT: Incorrect password.')
        return jsonify({'status': 'fail', 'message': 'Incorrect password.'}), 401

    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    print(f'{request.remote_addr} - POST /login ✅ RESULT: Login successful for "{username}"')
    print(f'🔐 JWT Token issued: {token}')

    return jsonify({
        'status': 'success',
        'message': f'Login successful for "{username}"',
        'token': token
    }), 200

@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    username = data.get('username', 'Unknown')

    print(f'👋 Logout received for "{username}". Session ended by client.')
    return jsonify({'status': 'success', 'message': f'Logout acknowledged for "{username}".'}), 200



if __name__ == '__main__':
    app.run(debug=True)
