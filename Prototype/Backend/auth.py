import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

try:
    from .database import get_connection
except ImportError:
    from database import get_connection


def create_user(username, password, role="inspector"):
    connection = get_connection()
    cursor = connection.cursor()

    password_hash = generate_password_hash(password)

    try:
        cursor.execute(
            """
            INSERT INTO users (
                username,
                password,
                role,
                active,
                created_at
            )
            VALUES (?, ?, ?, 1, ?)
            """,
            (
                username,
                password_hash,
                role,
                datetime.now().isoformat()
            )
        )

        connection.commit()

        return {
            "success": True,
            "user_id": cursor.lastrowid
        }

    except sqlite3.IntegrityError:
        return {
            "success": False,
            "error": "Username already exists"
        }

    finally:
        connection.close()


def authenticate_user(username, password):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        AND active = 1
        """,
        (username,)
    )

    user = cursor.fetchone()

    connection.close()

    if not user:
        return None

    if not check_password_hash(
        user["password"],
        password
    ):
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "active": bool(user["active"])
    }


def deactivate_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET active = 0
        WHERE id = ?
        """,
        (user_id,)
    )

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated


def activate_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET active = 1
        WHERE id = ?
        """,
        (user_id,)
    )

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated


def get_all_users():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            username,
            role,
            active,
            created_at
        FROM users
        ORDER BY created_at DESC
        """
    )

    users = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return users