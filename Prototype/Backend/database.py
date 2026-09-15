import sqlite3
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE = DATA_DIR / "sih26034.db"

DATA_DIR.mkdir(exist_ok=True)


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'inspector',
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT UNIQUE NOT NULL,
            product_name TEXT,
            product_type TEXT,
            package_type TEXT,
            image_path TEXT,
            extracted_text TEXT,
            overall_status TEXT,
            compliance_score REAL DEFAULT 0,
            readability_status TEXT,
            readability_confidence REAL DEFAULT 0,
            inspector_id INTEGER,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (inspector_id)
                REFERENCES users(id)
                ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            rule_id TEXT NOT NULL,
            field TEXT,
            description TEXT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (scan_id)
                REFERENCES scans(id)
                ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            report_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (scan_id)
                REFERENCES scans(id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()
    connection.close()


def create_scan(scan_data):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO scans (
            scan_id,
            product_name,
            product_type,
            package_type,
            image_path,
            extracted_text,
            overall_status,
            compliance_score,
            readability_status,
            readability_confidence,
            inspector_id,
            notes,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            scan_data["scan_id"],
            scan_data.get("product_name"),
            scan_data.get("product_type"),
            scan_data.get("package_type"),
            scan_data.get("image_path"),
            scan_data.get("extracted_text"),
            scan_data.get("overall_status"),
            scan_data.get("compliance_score", 0),
            scan_data.get("readability_status"),
            scan_data.get("readability_confidence", 0),
            scan_data.get("inspector_id"),
            scan_data.get("notes"),
            datetime.now().isoformat()
        )
    )

    database_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return database_id


def save_violation(scan_database_id, violation):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO violations (
            scan_id,
            rule_id,
            field,
            description,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            scan_database_id,
            violation.get("rule_id"),
            violation.get("field"),
            violation.get("description"),
            violation.get("status"),
            datetime.now().isoformat()
        )
    )

    connection.commit()
    connection.close()


def save_report(scan_database_id, report_type, file_path):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO reports (
            scan_id,
            report_type,
            file_path,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            scan_database_id,
            report_type,
            file_path,
            datetime.now().isoformat()
        )
    )

    connection.commit()
    connection.close()


def get_all_scans():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            scans.*,
            users.username AS inspector_username
        FROM scans
        LEFT JOIN users
            ON scans.inspector_id = users.id
        ORDER BY scans.created_at DESC
        """
    )

    scans = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return scans


def get_scan(scan_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            scans.*,
            users.username AS inspector_username
        FROM scans
        LEFT JOIN users
            ON scans.inspector_id = users.id
        WHERE scans.scan_id = ?
        """,
        (scan_id,)
    )

    scan = cursor.fetchone()

    connection.close()

    return dict(scan) if scan else None


def get_scan_violations(scan_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            violations.*
        FROM violations
        JOIN scans
            ON violations.scan_id = scans.id
        WHERE scans.scan_id = ?
        ORDER BY violations.created_at DESC
        """,
        (scan_id,)
    )

    violations = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return violations


def get_scan_reports(scan_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            reports.*
        FROM reports
        JOIN scans
            ON reports.scan_id = scans.id
        WHERE scans.scan_id = ?
        ORDER BY reports.created_at DESC
        """,
        (scan_id,)
    )

    reports = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return reports


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


def update_user_status(user_id, active):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET active = ?
        WHERE id = ?
        """,
        (
            1 if active else 0,
            user_id
        )
    )

    updated = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return updated


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at: {DATABASE}")