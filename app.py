import random
import re
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_PATH, JWT_SECRET, JWT_ALGORITHM, JWT_EXP_DELTA_SECONDS
from jwt import encode, decode
from flask_cors import CORS
from functools import wraps
from jwt import decode, ExpiredSignatureError, InvalidTokenError

app = Flask(__name__)
CORS(app)
app.secret_key = "magicmagicmagic"

# -----------------------------
# Database Initialization
# -----------------------------
def create_tables():
    """Create database tables if they don't exist."""
    with app.app_context():
        conn = get_db_connection()
        try:
            # Users table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Username TEXT UNIQUE NOT NULL,
                    PasswordHash TEXT NOT NULL
                )
            ''')
            # LaundryItems table (matches PyQt app)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS LaundryItems (
                    LaundryID INTEGER PRIMARY KEY,
                    Date TEXT,
                    Name TEXT,
                    CellNum TEXT,
                    TransactionType TEXT,
                    Kilos REAL,
                    Total REAL,
                    Status TEXT,
                    Remarks TEXT
                )
            ''')
            conn.commit()
        finally:
            conn.close()

def get_db_connection():
    """Get a database connection and enable foreign keys."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# Initialize database tables
create_tables()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return redirect(url_for('home'))
        try:
            token = token.split(" ")[1]
            payload = decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            session['user'] = payload['username']
        except (ExpiredSignatureError, InvalidTokenError):
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', username=session.get('user', 'User'))

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
        cursor.execute("INSERT INTO Users (Username, PasswordHash) VALUES (?, ?)",
                      (username, password_hash))
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT PasswordHash FROM Users WHERE Username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        return jsonify({'status': 'fail', 'message': 'Username not found.'}), 404
    stored_hash = result['PasswordHash']
    if not check_password_hash(stored_hash, password):
        return jsonify({'status': 'fail', 'message': 'Incorrect password.'}), 401
    # Generate JWT token
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    # Set session for template rendering
    session['user'] = username
    return jsonify({
        'status': 'success',
        'message': f'Login successful for "{username}"',
        'token': token
    }), 200

@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    username = data.get('username', 'Unknown')
    session.pop('user', None)
    return jsonify({'status': 'success', 'message': f'Logout acknowledged for "{username}".'}), 200

@app.route('/api/laundry', methods=['GET', 'POST'])
def api_laundry():
    """Add or fetch laundry items."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        contactnum = data.get('contactnum')
        transaction_type = data.get('transaction_type')
        remarks = data.get('remarks')

        try:
            kilos = float(data.get('kilos'))
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid kilos value"}), 400

        if not re.match(r"^[A-Za-z]+$", name):
            return jsonify({"error": "Name must contain only letters"}), 400
        if not re.match(r"^\d{3}-\d{3}-\d{4}$", contactnum):
            return jsonify({"error": "Phone number must be in XXX-XXX-XXXX format"}), 400

        total = 50 * kilos if transaction_type == 'Rush' else 40 * kilos
        status = "In progress"
        laundry_id = random.randint(1000, 9999)
        current_date = datetime.now().strftime("%Y-%m-%d")

        try:
            cursor.execute('''
                INSERT INTO LaundryItems
                (LaundryID, Date, Name, CellNum, TransactionType, Kilos, Total, Status, Remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (laundry_id, current_date, name, contactnum, transaction_type, kilos, total, status, remarks))
            conn.commit()
            return jsonify({"status": "success", "id": laundry_id})
        except Exception as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            conn.close()

    try:
        tab = request.args.get('tab', '0')
        item_id = request.args.get('id')

        if item_id:
            cursor.execute("SELECT * FROM LaundryItems WHERE LaundryID = ?", (item_id,))
        else:
            status = "In progress" if tab == "0" else "awaiting pick-up"
            cursor.execute("SELECT * FROM LaundryItems WHERE Status = ?", (status,))

        items = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return jsonify([dict(zip(columns, row)) for row in items])
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()

@app.route('/api/laundry/laundry/<int:item_id>', methods=['GET'])
def get_laundry_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM LaundryItems WHERE LaundryID = ?", (item_id,))
        items = cursor.fetchall()
        if not items:
            return jsonify({"error": "Item not found"}), 404
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in items]
        return jsonify({"status": "success", "laundry": len(result), "0": result[0]})
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()

@app.route('/api/laundry/<int:item_id>', methods=['PUT', 'DELETE'])
def update_delete_item(item_id):
    """Update or delete a laundry item."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if request.method == 'PUT':
            data = request.json
            new_status = data.get('status')
            new_name = data.get('name')
            new_contact = data.get('contactnum')
            new_transact_type = data.get('transaction_type')
            new_remarks = data.get('remarks')
            kilos = float(data.get('kilos'))
            total = 50 * kilos if new_transact_type == 'Rush' else 40 * kilos
            cursor.execute('''
                UPDATE LaundryItems
                SET Status = ?, TransactionType = ?, Total = ?, Name = ?,
                    Remarks = ?, CellNum = ?, Kilos = ?
                WHERE LaundryID = ?
            ''', (new_status, new_transact_type, total, new_name, new_remarks, new_contact, kilos, item_id))
            conn.commit()
            return jsonify({"status": "updated"})
        elif request.method == 'DELETE':
            cursor.execute("DELETE FROM LaundryItems WHERE LaundryID = ?", (item_id,))
            conn.commit()
            return jsonify({"status": "deleted"})
    except Exception as e:
        return jsonify({"error": f"Operation failed: {str(e)}"}), 500
    finally:
        conn.close()

@app.route('/api/laundry/combo')
def get_combo_items():
    """Fetch LaundryIDs for combo box."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT LaundryID FROM LaundryItems WHERE Status IN ('awaiting pick-up', 'In progress')")
        ids = [row['LaundryID'] for row in cursor.fetchall()]
        return jsonify(ids)
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)