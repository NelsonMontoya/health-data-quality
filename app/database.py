import duckdb
from datetime import datetime

class AuditDatabase:
    def __init__(self, db_path="data_audit.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        """Crea la tabla de auditoría si no existe."""
        with duckdb.connect(self.db_path) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS audit_history (
                    timestamp TIMESTAMP,
                    country_name TEXT,
                    indicator_name TEXT,
                    health_score DOUBLE,
                    total_records INTEGER,
                    anomalies_count INTEGER
                )
            """)

    def save_audit(self, country, indicator, score, total, anomalies):
        """Guarda el resultado de una auditoría."""
        with duckdb.connect(self.db_path) as con:
            con.execute("""
                INSERT INTO audit_history VALUES (?, ?, ?, ?, ?, ?)
            """, (datetime.now(), country, indicator, score, total, anomalies))

    def get_history(self):
        """Recupera todo el historial de auditorías."""
        with duckdb.connect(self.db_path) as con:
            return con.execute("SELECT * FROM audit_history ORDER BY timestamp DESC").df()