import duckdb
import pandas as pd
from datetime import datetime

class AuditDatabase:
    def __init__(self, db_path='data_audit.db'):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        with duckdb.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    timestamp TIMESTAMP,
                    country_name VARCHAR,
                    indicator_name VARCHAR,
                    health_score DOUBLE,
                    total_records INTEGER,
                    anomalies_count INTEGER
                )
            """)

    def save_audit(self, country, indicator, score, total, anomalies):
        with duckdb.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO audit_logs VALUES (?, ?, ?, ?, ?, ?)
            """, (datetime.now(), country, indicator, score, total, anomalies))

    def get_history(self):
        with duckdb.connect(self.db_path) as conn:
            return conn.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC").df()