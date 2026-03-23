"""
VitaSense AI - models.py
Database setup using SQLite.
Tables: predictions, chat_history
"""

import sqlite3
import os

# ─── Database path ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "vitasense.db")


def get_db_connection():
    """Returns a new SQLite connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates all tables if they don't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # ── Table 1: predictions ──────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,

            -- Input fields (required)
            glucose             REAL NOT NULL,
            blood_pressure      REAL NOT NULL,
            bmi                 REAL NOT NULL,
            dpf                 REAL NOT NULL,
            age                 REAL NOT NULL,

            -- Input fields (optional — NULL if not provided)
            pregnancies         REAL,
            skin_thickness      REAL,
            insulin             REAL,

            -- Core prediction result
            prediction          TEXT NOT NULL,          -- 'Diabetic' | 'Not Diabetic'
            risk_percentage     REAL NOT NULL,          -- 0.0 – 100.0
            risk_level          TEXT NOT NULL,          -- 'Low' | 'Medium' | 'High'
            risk_category       TEXT NOT NULL,          -- 'Normal' | 'Prediabetes' | 'Diabetes'

            -- Detailed health metrics
            hba1c_estimate      REAL,                   -- % estimated from glucose
            bmi_status          TEXT,                   -- 'Underweight'|'Normal'|'Overweight'|'Obese'
            glucose_category    TEXT,                   -- 'Normal'|'Prediabetes'|'High'
            bp_status           TEXT,                   -- 'Normal'|'Elevated'|'High'
            age_risk_factor     REAL,                   -- % contribution
            insulin_resistance  REAL,                   -- HOMA-IR estimate
            health_score        REAL,                   -- 0 – 100

            -- Percentage contributions (for detailed breakdown)
            glucose_contribution    REAL,
            bmi_contribution        REAL,
            age_contribution        REAL,
            dpf_contribution        REAL,
            bp_contribution         REAL,

            -- Recommendation message
            urgency_level       TEXT,                   -- 'See Doctor Now'|'See Doctor Soon'|'Routine Checkup'
            recommendation_msg  TEXT                    -- personalised message based on risk
        )
    """)

    # ── Table 2: chat_history ─────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            topic        TEXT                            -- detected topic keyword
        )
    """)

    conn.commit()
    conn.close()
    print("✓ Database initialised — vitasense.db created with 2 tables.")


# ─── Helper: save a prediction record ─────────────────────────────────────────
def save_prediction(data: dict) -> int:
    """
    Inserts a prediction result into the predictions table.
    Returns the new row id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO predictions (
            glucose, blood_pressure, bmi, dpf, age,
            pregnancies, skin_thickness, insulin,
            prediction, risk_percentage, risk_level, risk_category,
            hba1c_estimate, bmi_status, glucose_category, bp_status,
            age_risk_factor, insulin_resistance, health_score,
            glucose_contribution, bmi_contribution, age_contribution,
            dpf_contribution, bp_contribution,
            urgency_level, recommendation_msg
        ) VALUES (
            :glucose, :blood_pressure, :bmi, :dpf, :age,
            :pregnancies, :skin_thickness, :insulin,
            :prediction, :risk_percentage, :risk_level, :risk_category,
            :hba1c_estimate, :bmi_status, :glucose_category, :bp_status,
            :age_risk_factor, :insulin_resistance, :health_score,
            :glucose_contribution, :bmi_contribution, :age_contribution,
            :dpf_contribution, :bp_contribution,
            :urgency_level, :recommendation_msg
        )
    """, data)
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


# ─── Helper: save a chat message ──────────────────────────────────────────────
def save_chat(user_message: str, bot_response: str, topic: str = None) -> int:
    """Inserts a chat exchange into chat_history. Returns the new row id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_history (user_message, bot_response, topic)
        VALUES (?, ?, ?)
    """, (user_message, bot_response, topic))
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


# ─── Helper: fetch recent predictions ─────────────────────────────────────────
def get_recent_predictions(limit: int = 10) -> list:
    """Returns the most recent N predictions as a list of dicts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM predictions
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# ─── Helper: fetch dashboard stats ────────────────────────────────────────────
def get_dashboard_stats() -> dict:
    """Returns aggregated stats for the Dashboard tab."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM predictions")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as cnt FROM predictions WHERE prediction = 'Diabetic'")
    diabetic = cursor.fetchone()["cnt"]

    cursor.execute("SELECT AVG(risk_percentage) as avg_risk FROM predictions")
    avg_risk = cursor.fetchone()["avg_risk"] or 0.0

    cursor.execute("SELECT AVG(health_score) as avg_health FROM predictions")
    avg_health = cursor.fetchone()["avg_health"] or 0.0

    cursor.execute("""
        SELECT risk_level, COUNT(*) as cnt
        FROM predictions
        GROUP BY risk_level
    """)
    risk_dist = {row["risk_level"]: row["cnt"] for row in cursor.fetchall()}

    conn.close()
    return {
        "total_predictions": total,
        "diabetic_count":    diabetic,
        "non_diabetic_count": total - diabetic,
        "avg_risk_percentage": round(avg_risk, 1),
        "avg_health_score":    round(avg_health, 1),
        "risk_distribution":   risk_dist,
    }


# ─── Run directly to initialise DB ────────────────────────────────────────────
if __name__ == "__main__":
    init_db()