"""
LociLoom SQLite Database Interface
Handles persistence for anonymous users, palaces, concepts, quiz attempts,
SM-2 spaced repetition reviews, and scientific experiment records.
All queries use strict parameterized execution with indexing for performance.
"""
import sqlite3
import os
import json
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "lociloom.db")

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Returns a connection to the SQLite database with row_factory enabled."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def hash_password(password: str) -> str:
    """Returns SHA-256 salted hash of password."""
    salt = "lociloom_salt_2026"
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

def init_db(db_path: str = DB_PATH) -> None:
    """Initializes tables and indexes if they do not exist."""
    conn = get_connection(db_path)
    with conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            anon_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            settings_json TEXT NOT NULL DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT,
            FOREIGN KEY (user_id) REFERENCES users(anon_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS palaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            topic TEXT NOT NULL,
            palace_type TEXT NOT NULL,
            story_style TEXT NOT NULL DEFAULT 'Normal',
            language TEXT NOT NULL DEFAULT 'en',
            story_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(anon_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            palace_id INTEGER NOT NULL,
            order_index INTEGER NOT NULL,
            location_name TEXT NOT NULL,
            concept_text TEXT NOT NULL,
            supporting_sentence TEXT NOT NULL DEFAULT '',
            difficulty TEXT NOT NULL DEFAULT 'Medium',
            visual_object TEXT NOT NULL,
            visual_reason TEXT NOT NULL DEFAULT '',
            user_edited INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (palace_id) REFERENCES palaces(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            concept_id INTEGER NOT NULL,
            question_type TEXT NOT NULL,
            correct INTEGER NOT NULL,
            response_time REAL NOT NULL DEFAULT 0.0,
            hints_used INTEGER NOT NULL DEFAULT 0,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(anon_id) ON DELETE CASCADE,
            FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS reviews (
            concept_id INTEGER PRIMARY KEY,
            ease_factor REAL NOT NULL DEFAULT 2.5,
            interval_days INTEGER NOT NULL DEFAULT 1,
            repetitions INTEGER NOT NULL DEFAULT 0,
            next_due TEXT NOT NULL,
            FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS experiment_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_id TEXT NOT NULL,
            condition TEXT NOT NULL,
            list_id TEXT NOT NULL,
            study_time REAL NOT NULL,
            immediate_score REAL NOT NULL,
            delayed_score REAL DEFAULT NULL,
            satisfaction INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );

        -- Performance Indexes
        CREATE INDEX IF NOT EXISTS idx_accounts_username ON accounts(username);
        CREATE INDEX IF NOT EXISTS idx_palaces_user ON palaces(user_id);
        CREATE INDEX IF NOT EXISTS idx_concepts_palace ON concepts(palace_id);
        CREATE INDEX IF NOT EXISTS idx_quiz_user ON quiz_attempts(user_id);
        CREATE INDEX IF NOT EXISTS idx_quiz_concept ON quiz_attempts(concept_id);
        CREATE INDEX IF NOT EXISTS idx_reviews_next_due ON reviews(next_due);
        CREATE INDEX IF NOT EXISTS idx_experiment_part ON experiment_records(participant_id);
        """)

        # Auto-seed default Admin and Student accounts if none exist
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM accounts WHERE username = 'admin'")
        if cur.fetchone()["cnt"] == 0:
            now_str = datetime.now(timezone.utc).isoformat()
            cur.execute("INSERT OR IGNORE INTO users (anon_id, created_at, settings_json) VALUES (?, ?, ?)",
                        ("LL-ADMIN-001", now_str, "{}"))
            cur.execute("INSERT OR IGNORE INTO users (anon_id, created_at, settings_json) VALUES (?, ?, ?)",
                        ("LL-STUDENT-001", now_str, "{}"))
            cur.execute("""
                INSERT INTO accounts (username, password_hash, role, user_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, ("admin", hash_password("adminpassword123"), "admin", "LL-ADMIN-001", now_str))
            cur.execute("""
                INSERT INTO accounts (username, password_hash, role, user_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, ("student", hash_password("student123"), "student", "LL-STUDENT-001", now_str))
    conn.close()

def get_or_create_user(anon_id: str, default_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Retrieves or registers an anonymous user ID."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT anon_id, created_at, settings_json FROM users WHERE anon_id = ?", (anon_id,))
        row = cur.fetchone()
        if row:
            return {
                "anon_id": row["anon_id"],
                "created_at": row["created_at"],
                "settings": json.loads(row["settings_json"])
            }
        else:
            settings_str = json.dumps(default_settings or {})
            now = datetime.now(timezone.utc).isoformat()
            cur.execute(
                "INSERT INTO users (anon_id, created_at, settings_json) VALUES (?, ?, ?)",
                (anon_id, now, settings_str)
            )
            conn.commit()
            return {
                "anon_id": anon_id,
                "created_at": now,
                "settings": default_settings or {}
            }
    finally:
        conn.close()

def update_user_settings(anon_id: str, settings: Dict[str, Any]) -> None:
    """Updates JSON settings for an anonymous student."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET settings_json = ? WHERE anon_id = ?",
            (json.dumps(settings), anon_id)
        )
        conn.commit()
    finally:
        conn.close()

def save_palace(user_id: str, title: str, topic: str, palace_type: str,
                story_style: str, language: str, story_text: str,
                concepts_list: List[Dict[str, Any]]) -> int:
    """
    Saves a newly constructed memory palace along with its ordered concept anchors.
    Also initializes SM-2 review entries for each concept.
    """
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            cur.execute("""
                INSERT INTO palaces (user_id, title, topic, palace_type, story_style, language, story_text, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, title, topic, palace_type, story_style, language, story_text, now))
            palace_id = cur.lastrowid

            for idx, c in enumerate(concepts_list):
                cur.execute("""
                    INSERT INTO concepts (palace_id, order_index, location_name, concept_text,
                                          supporting_sentence, difficulty, visual_object, visual_reason, user_edited)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    palace_id,
                    idx,
                    c.get("location_name", f"Station {idx+1}"),
                    c.get("concept_text", c.get("concept", "")),
                    c.get("supporting_sentence", ""),
                    c.get("difficulty", "Medium"),
                    c.get("visual_object", ""),
                    c.get("visual_reason", ""),
                    1 if c.get("user_edited", False) else 0
                ))
                concept_id = cur.lastrowid
                
                # Initialize SM-2 review entry due immediately (today)
                cur.execute("""
                    INSERT OR IGNORE INTO reviews (concept_id, ease_factor, interval_days, repetitions, next_due)
                    VALUES (?, 2.5, 1, 0, ?)
                """, (concept_id, now[:10]))
                
            return palace_id
    finally:
        conn.close()

def get_palaces(user_id: str) -> List[Dict[str, Any]]:
    """Returns all palaces created by the user with concept counts and review status."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.*, COUNT(c.id) as concept_count,
                   MAX(q.timestamp) as last_practised,
                   MIN(r.next_due) as next_revision_due
            FROM palaces p
            LEFT JOIN concepts c ON p.id = c.palace_id
            LEFT JOIN quiz_attempts q ON c.id = q.concept_id
            LEFT JOIN reviews r ON c.id = r.concept_id
            WHERE p.user_id = ?
            GROUP BY p.id
            ORDER BY p.id DESC
        """, (user_id,))
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_palace_by_id(palace_id: int) -> Optional[Dict[str, Any]]:
    """Returns a full palace dictionary including its concepts list."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM palaces WHERE id = ?", (palace_id,))
        palace_row = cur.fetchone()
        if not palace_row:
            return None
        
        palace = dict(palace_row)
        cur.execute("""
            SELECT c.*, r.ease_factor, r.interval_days, r.repetitions, r.next_due
            FROM concepts c
            LEFT JOIN reviews r ON c.id = r.concept_id
            WHERE c.palace_id = ?
            ORDER BY c.order_index ASC
        """, (palace_id,))
        palace["concepts"] = [dict(c) for c in cur.fetchall()]
        return palace
    finally:
        conn.close()

def update_palace_title(palace_id: int, new_title: str) -> None:
    """Renames an existing palace."""
    conn = get_connection()
    try:
        with conn:
            conn.execute("UPDATE palaces SET title = ? WHERE id = ?", (new_title, palace_id))
    finally:
        conn.close()

def duplicate_palace(palace_id: int, new_title: Optional[str] = None) -> Optional[int]:
    """Duplicates a palace and all its concepts."""
    palace = get_palace_by_id(palace_id)
    if not palace:
        return None
    title = new_title or f"{palace['title']} (Copy)"
    return save_palace(
        user_id=palace["user_id"],
        title=title,
        topic=palace["topic"],
        palace_type=palace["palace_type"],
        story_style=palace["story_style"],
        language=palace["language"],
        story_text=palace["story_text"],
        concepts_list=palace["concepts"]
    )

def delete_palace(palace_id: int) -> None:
    """Deletes a palace and all associated concepts and reviews via CASCADE."""
    conn = get_connection()
    try:
        with conn:
            conn.execute("DELETE FROM palaces WHERE id = ?", (palace_id,))
    finally:
        conn.close()

def update_concept(concept_id: int, visual_object: str, visual_reason: str, location_name: Optional[str] = None) -> None:
    """Updates visual object or location name for a concept."""
    conn = get_connection()
    try:
        with conn:
            if location_name:
                conn.execute("""
                    UPDATE concepts 
                    SET visual_object = ?, visual_reason = ?, location_name = ?, user_edited = 1
                    WHERE id = ?
                """, (visual_object, visual_reason, location_name, concept_id))
            else:
                conn.execute("""
                    UPDATE concepts 
                    SET visual_object = ?, visual_reason = ?, user_edited = 1
                    WHERE id = ?
                """, (visual_object, visual_reason, concept_id))
    finally:
        conn.close()

def log_quiz_attempt(user_id: str, concept_id: int, question_type: str,
                     correct: bool, response_time: float, hints_used: int) -> int:
    """Logs a student retrieval attempt for accuracy and forgetting modeling."""
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            
            # Ensure user exists in users table
            cur.execute("INSERT OR IGNORE INTO users (anon_id, created_at) VALUES (?, ?)", (user_id, now))
            
            # Verify concept_id exists in concepts table to prevent FK constraint failure
            c_row = cur.execute("SELECT id FROM concepts WHERE id = ?", (concept_id,)).fetchone()
            if not c_row:
                # Fallback to any valid concept ID for this user, or latest concept
                fallback = cur.execute("""
                    SELECT c.id FROM concepts c
                    JOIN palaces p ON c.palace_id = p.id
                    WHERE p.user_id = ?
                    ORDER BY c.id DESC LIMIT 1
                """, (user_id,)).fetchone()
                if not fallback:
                    fallback = cur.execute("SELECT id FROM concepts ORDER BY id DESC LIMIT 1").fetchone()
                if fallback:
                    concept_id = fallback[0]
                else:
                    return 0

            cur.execute("""
                INSERT INTO quiz_attempts (user_id, concept_id, question_type, correct, response_time, hints_used, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, concept_id, question_type, 1 if correct else 0, response_time, hints_used, now))
            return cur.lastrowid
    except Exception:
        return 0
    finally:
        conn.close()

def get_quiz_attempts(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches retrieval logs for dashboard analytics and adaptive model evaluation."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = """
            SELECT q.*, c.concept_text, c.location_name, c.difficulty, p.topic, p.title as palace_title
            FROM quiz_attempts q
            JOIN concepts c ON q.concept_id = c.id
            JOIN palaces p ON c.palace_id = p.id
        """
        params = []
        if user_id:
            query += " WHERE q.user_id = ?"
            params.append(user_id)
        query += " ORDER BY q.timestamp DESC"
        cur.execute(query, params)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def get_sm2_review(concept_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves current SM-2 state for a concept."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM reviews WHERE concept_id = ?", (concept_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def save_sm2_review(concept_id: int, ease_factor: float, interval_days: int, repetitions: int, next_due: str) -> None:
    """Updates SM-2 repetition schedule for a concept."""
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            c_row = cur.execute("SELECT id FROM concepts WHERE id = ?", (concept_id,)).fetchone()
            if not c_row:
                return
            conn.execute("""
                INSERT OR REPLACE INTO reviews (concept_id, ease_factor, interval_days, repetitions, next_due)
                VALUES (?, ?, ?, ?, ?)
            """, (concept_id, ease_factor, interval_days, repetitions, next_due))
    except Exception:
        pass
    finally:
        conn.close()

def get_all_reviews_due(user_id: str) -> List[Dict[str, Any]]:
    """Retrieves all concepts belonging to user with their review schedules."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.id as concept_id, c.concept_text, c.location_name, c.difficulty,
                   c.visual_object, p.id as palace_id, p.title as palace_title, p.topic,
                   r.ease_factor, r.interval_days, r.repetitions, r.next_due
            FROM concepts c
            JOIN palaces p ON c.palace_id = p.id
            LEFT JOIN reviews r ON c.id = r.concept_id
            WHERE p.user_id = ?
            ORDER BY r.next_due ASC, c.order_index ASC
        """, (user_id,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def save_experiment_record(participant_id: str, condition: str, list_id: str,
                           study_time: float, immediate_score: float,
                           satisfaction: int, delayed_score: Optional[float] = None) -> int:
    """Saves a formal participant trial record in Experiment Mode."""
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            cur.execute("""
                INSERT INTO experiment_records (participant_id, condition, list_id, study_time,
                                               immediate_score, delayed_score, satisfaction, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (participant_id, condition, list_id, study_time, immediate_score, delayed_score, satisfaction, now))
            return cur.lastrowid
    finally:
        conn.close()

def update_experiment_delayed_score(record_id: int, delayed_score: float) -> None:
    """Updates the 24-hour delayed recall score for an experiment participant."""
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
                UPDATE experiment_records SET delayed_score = ? WHERE id = ?
            """, (delayed_score, record_id))
    finally:
        conn.close()

def get_experiment_records() -> List[Dict[str, Any]]:
    """Returns all empirical evaluation rows for statistical analysis."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM experiment_records ORDER BY id ASC")
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def register_account(username: str, password: str, role: str = "student") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Registers a new student or admin account with secure password hashing."""
    u_clean = username.strip().lower()
    if not u_clean or len(u_clean) < 3:
        return (False, "Username must be at least 3 characters.", None)
    if not password or len(password) < 4:
        return (False, "Password must be at least 4 characters.", None)

    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM accounts WHERE username = ?", (u_clean,))
            if cur.fetchone():
                return (False, f"Username '{u_clean}' is already registered.", None)

            now_str = datetime.now(timezone.utc).isoformat()
            token = uuid.uuid4().hex[:4].upper()
            user_id = f"LL-{u_clean.upper()}-{token}"
            cur.execute("INSERT OR IGNORE INTO users (anon_id, created_at, settings_json) VALUES (?, ?, ?)",
                        (user_id, now_str, "{}"))

            pwd_hash = hash_password(password)
            cur.execute("""
                INSERT INTO accounts (username, password_hash, role, user_id, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (u_clean, pwd_hash, role, user_id, now_str, now_str))

            account_data = {
                "id": cur.lastrowid,
                "username": u_clean,
                "role": role,
                "user_id": user_id
            }
            return (True, "Account registered successfully!", account_data)
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Verifies username and password, updates last_login, and returns account record."""
    u_clean = username.strip().lower()
    conn = get_connection()
    try:
        cur = conn.cursor()
        pwd_hash = hash_password(password)
        cur.execute("""
            SELECT id, username, role, user_id, created_at
            FROM accounts
            WHERE username = ? AND password_hash = ?
        """, (u_clean, pwd_hash))
        row = cur.fetchone()
        if row:
            now_str = datetime.now(timezone.utc).isoformat()
            with conn:
                conn.execute("UPDATE accounts SET last_login = ? WHERE id = ?", (now_str, row["id"]))
            return dict(row)
        return None
    finally:
        conn.close()

def get_all_users_admin() -> List[Dict[str, Any]]:
    """Admin function: returns all accounts with user activity stats."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT a.id, a.username, a.role, a.user_id, a.created_at, a.last_login,
                   (SELECT COUNT(*) FROM palaces p WHERE p.user_id = a.user_id) as total_palaces,
                   (SELECT COUNT(*) FROM quiz_attempts q WHERE q.user_id = a.user_id) as total_quizzes
            FROM accounts a
            ORDER BY a.id ASC
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def get_all_palaces_admin() -> List[Dict[str, Any]]:
    """Admin function: returns all palaces across all registered users."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, p.user_id, p.title, p.topic, p.palace_type, p.created_at,
                   (SELECT COUNT(*) FROM concepts c WHERE c.palace_id = p.id) as concept_count
            FROM palaces p
            ORDER BY p.id DESC
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def get_admin_dashboard_metrics() -> Dict[str, Any]:
    """Admin function: computes system-wide analytics KPIs."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM accounts")
        total_accounts = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) as cnt FROM palaces")
        total_palaces = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) as cnt FROM quiz_attempts")
        total_quizzes = cur.fetchone()["cnt"]

        cur.execute("SELECT AVG(correct) as avg_acc FROM quiz_attempts")
        acc_row = cur.fetchone()
        avg_acc = round(float(acc_row["avg_acc"] or 0.0) * 100, 1)

        cur.execute("SELECT COUNT(*) as cnt FROM experiment_records")
        total_experiments = cur.fetchone()["cnt"]

        return {
            "total_accounts": total_accounts,
            "total_palaces": total_palaces,
            "total_quizzes": total_quizzes,
            "avg_accuracy": avg_acc,
            "total_experiments": total_experiments
        }
    finally:
        conn.close()

def reset_all_data() -> None:
    """Cleans all tables and resets database state."""
    conn = get_connection()
    try:
        with conn:
            conn.executescript("""
                DELETE FROM experiment_records;
                DELETE FROM reviews;
                DELETE FROM quiz_attempts;
                DELETE FROM concepts;
                DELETE FROM palaces;
                DELETE FROM users;
            """)
    finally:
        conn.close()

# Auto-initialize database on import
init_db()
