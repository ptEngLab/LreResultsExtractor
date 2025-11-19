import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Iterator, Dict, Any, Optional
from lre_client.utils.logger import get_logger

log = get_logger(__name__)


def optimize_connection(conn: sqlite3.Connection):
    """Apply safe performance optimizations for large read-only queries."""
    pragma_list = [
        ("cache_size", "-100000"),      # ~100MB
        ("page_size", "4096"),
        ("mmap_size", "268435456"),     # 256MB
        ("temp_store", "MEMORY"),
        ("optimize", None),
    ]

    for pragma, value in pragma_list:
        if value is None:
            conn.execute(f"PRAGMA {pragma};")
        else:
            conn.execute(f"PRAGMA {pragma}={value};")


class DatabaseManager:
    def __init__(self):
        self._db_path: Optional[Path] = None

    def connect(self, db_file: str) -> str:
        """Validate database file exists and is accessible"""
        db_path = Path(db_file).resolve()

        if not db_path.exists():
            raise FileNotFoundError(f"SQLite DB not found: {db_path}")

        if not os.access(db_path, os.R_OK):
            raise PermissionError(f"No read permission for database: {db_path}")

        self._db_path = db_path
        log.debug(f"Database file validated: {db_path}")
        return f"Database file validated: {db_path}"

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """Context manager for read-only database connections."""
        if not self._db_path:
            raise ConnectionError("No database file specified. Call connect() first.")

        # Open read-only
        conn = sqlite3.connect(f"file:{self._db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row

        try:
            optimize_connection(conn)
            yield conn
        finally:
            conn.close()

    def execute_query(self, sql: str, params: tuple = ()) -> Iterator[Dict[str, Any]]:
        """
        Execute query and stream results one-by-one.
        Constant memory footprint regardless of result set size.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)

            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                yield dict(row)

    # Helper methods using streaming internally
    def get_first(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Get only the first result from a query."""
        for row in self.execute_query(sql, params):
            return row
        return None

    def get_all(self, sql: str, params: tuple = ()) -> list[Dict[str, Any]]:
        """Get all results (only for small result sets)."""
        return list(self.execute_query(sql, params))

    def get_count(self, sql: str, params: tuple = ()) -> int:
        """Execute COUNT query and return integer result."""
        result = self.get_first(sql, params)
        return result['count'] if result else 0

    # Metadata helpers
    def get_table_info(self, table_name: str) -> list[Dict[str, Any]]:
        return self.get_all(f"PRAGMA table_info({table_name})")

    def get_table_names(self) -> list[str]:
        return [row['name'] for row in self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )]

    def estimate_row_count(self, table_name: str) -> int:
        return self.get_count(f"SELECT COUNT(*) AS count FROM {table_name}")
