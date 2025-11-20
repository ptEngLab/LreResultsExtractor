import sqlite3
import pandas as pd
from typing import Optional, Dict, Any, Iterator
from contextlib import contextmanager
from lre_client.utils.logger import get_logger

log = get_logger(__name__)


def _optimize_connection(conn: sqlite3.Connection):
    """Apply performance optimizations for large read-only queries."""
    pragma_list = [
        ("journal_mode", "MEMORY"),    # Reduce I/O for read-heavy workloads
        ("cache_size", "-100000"),     # ~100MB cache
        ("page_size", "4096"),         # Optimal page size
        ("mmap_size", "268435456"),    # 256MB memory mapping
        ("temp_store", "MEMORY"),      # Store temp tables in memory
        ("synchronous", "NORMAL"),     # Balance safety vs performance
        ("locking_mode", "NORMAL"),
    ]

    try:
        for pragma, value in pragma_list:
            conn.execute(f"PRAGMA {pragma}={value};")

        # Run optimization
        conn.execute("PRAGMA optimize;")
        log.debug("Applied SQLite performance optimizations")

    except sqlite3.Error as e:
        log.warning(f"SQLite optimizations partially failed: {e}")


class SQLiteDBManager:
    """
    High-performance SQLite database manager optimized for large read-only analytics.
    """

    def __init__(self, db_path: str, timeout: int = 30, default_chunk_size: int = 50_000):
        self.db_path = db_path
        self.timeout = timeout
        self.default_chunk_size = default_chunk_size
        self._conn: Optional[sqlite3.Connection] = None

    @contextmanager
    def connection(self):
        """Context manager for database connection with optimizations."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=self.timeout)
            conn.row_factory = sqlite3.Row
            _optimize_connection(conn)
            log.debug("Database connection established and optimized")
            yield conn
        except sqlite3.Error as e:
            log.error(f"Database connection failed: {e}")
            raise
        finally:
            if conn:
                conn.close()
                log.debug("Database connection closed")

    def query(
            self,
            sql: str,
            params: Optional[Dict[str, Any]] = None,
            chunk_size: Optional[int] = None
    ) -> Iterator[pd.DataFrame]:
        """
        Unified query method that always uses chunked processing.
        """
        actual_chunk_size = chunk_size if chunk_size is not None else self.default_chunk_size

        with self.connection() as conn:
            log.debug(f"Executing query with chunk size {actual_chunk_size}")
            yield from pd.read_sql_query(sql, conn, params=params, chunksize=actual_chunk_size)

    def query_single(
            self,
            sql: str,
            params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Convenience method for when you want a single DataFrame.
        Still uses chunked processing internally but returns combined result.
        """
        log.debug(f"Executing single-result query: {sql[:100]}...")
        chunks = self.query(sql, params, chunk_size=None)
        result_chunks = []

        for chunk in chunks:
            result_chunks.append(chunk)

        if result_chunks:
            result = pd.concat(result_chunks, ignore_index=True)
            log.debug(f"Single query returned {len(result)} rows")
            return result
        else:
            log.debug("Single query returned empty result")
            return pd.DataFrame()