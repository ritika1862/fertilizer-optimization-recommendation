import sqlite3
import hashlib
from pathlib import Path


# Database location
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "fertilizer.db"


def get_connection():
    """Create and return a database connection."""
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create required tables if they do not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Recommendations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            crop TEXT NOT NULL,
            nitrogen REAL,
            phosphorus REAL,
            potassium REAL,
            soil_ph REAL,
            budget REAL,
            recommended_fertilizer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    """Convert password into a secure hash."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(name, email, password):
    """Create a new user account."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        hashed_password = hash_password(password)

        cursor.execute("""
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        """, (name, email, hashed_password))

        conn.commit()
        return True, "Account created successfully!"

    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."

    except Exception as e:
        return False, f"Error: {e}"

    finally:
        conn.close()


def authenticate_user(email, password):
    """Check login credentials."""
    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    cursor.execute("""
        SELECT id, name, email
        FROM users
        WHERE email = ? AND password = ?
    """, (email, hashed_password))

    user = cursor.fetchone()

    conn.close()

    if user:
        return {
            "id": user[0],
            "name": user[1],
            "email": user[2]
        }

    return None


def save_recommendation(
    user_id,
    crop,
    nitrogen,
    phosphorus,
    potassium,
    soil_ph,
    budget,
    recommended_fertilizer
):
    """Save a fertilizer recommendation."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO recommendations (
            user_id,
            crop,
            nitrogen,
            phosphorus,
            potassium,
            soil_ph,
            budget,
            recommended_fertilizer
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        crop,
        nitrogen,
        phosphorus,
        potassium,
        soil_ph,
        budget,
        recommended_fertilizer
    ))

    conn.commit()
    conn.close()


def get_user_recommendations(user_id):
    """Get all recommendations made by a user."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            crop,
            nitrogen,
            phosphorus,
            potassium,
            soil_ph,
            budget,
            recommended_fertilizer,
            created_at
        FROM recommendations
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))

    recommendations = cursor.fetchall()

    conn.close()

    return recommendations


# Initialize database automatically
initialize_database()