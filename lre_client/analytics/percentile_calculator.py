import pandas as pd
from typing import Dict, Tuple
from lre_client.utils.logger import get_logger
from tdigest import TDigest

from lre_client.db.database_manager import  SQLiteDBManager
from lre_client.db.query_store import QueryStore

log = get_logger(__name__)


class PercentileCalculator:
    """Production-grade percentile calculator using optimized chunked processing."""

    def __init__(self, db_path: str, chunksize: int = 100_000):
        self.db_path = db_path
        self.chunksize = chunksize

    def _compute_percentiles(self) -> pd.DataFrame:
        """Optimized streaming percentile computation using unified chunked processing."""


        digests: Dict[Tuple[str, str], TDigest] = {}
        total_processed = 0
        method_used = "vectorized"

        with SQLiteDBManager(self.db_path, default_chunk_size=self.chunksize) as db:
            # Unified chunked processing with optimizations always applied
            for chunk in db.query(QueryStore.SQL_TRANSACTION_RESPONSE_TIMES):
                total_processed += len(chunk)

                # Data is already filtered by SQL, but double-check
                mask = (chunk["Response_Times"] > 0) & (chunk["Counts"] > 0)
                chunk = chunk[mask]

                if chunk.empty:
                    continue

                # Vectorized group processing with fallback
                try:
                    for (script, txn), group in chunk.groupby(["Script_Name", "Transaction_Name"]):
                        if (script, txn) not in digests:
                            digests[(script, txn)] = TDigest()

                        rt_values = group["Response_Times"].to_numpy()
                        counts = group["Counts"].to_numpy()

                        # Use batch_update if available
                        if hasattr(digests[(script, txn)], "batch_update"):
                            digests[(script, txn)].batch_update(rt_values, counts)
                        else:
                            method_used = "iterative"
                            for rt, count in zip(rt_values, counts):
                                digests[(script, txn)].update(rt, count)

                except (AttributeError, TypeError) as e:
                    # Full fallback: row-by-row
                    method_used = "fallback"
                    for _, row in chunk.iterrows():
                        script, txn = row["Script_Name"], row["Transaction_Name"]
                        rt, count = row["Response_Times"], row["Counts"]
                        if (script, txn) not in digests:
                            digests[(script, txn)] = TDigest()
                        digests[(script, txn)].update(rt, count)

        log.info(f"Processed {total_processed:,} rows using {method_used} method")
        log.info(f"Computed percentiles for {len(digests):,} transaction groups")

        return self._build_results(digests)

    def _build_results(self, digests: Dict[Tuple[str, str], TDigest]) -> pd.DataFrame:
        """Build final percentile DataFrame with validation."""
        results = []
        for (script, txn), d in digests.items():
            # Validate percentiles
            p50 = d.percentile(50)
            p90 = d.percentile(90)
            p95 = d.percentile(95)
            p99 = d.percentile(99)

            results.append({
                "Script_Name": script,
                "Transaction_Name": txn,
                "p50": p50 if not pd.isna(p50) and p50 > 0 else 0.0,
                "p90": p90 if not pd.isna(p90) and p90 > 0 else 0.0,
                "p95": p95 if not pd.isna(p95) and p95 > 0 else 0.0,
                "p99": p99 if not pd.isna(p99) and p99 > 0 else 0.0,
            })

        return pd.DataFrame(results)

    def compute_percentiles(self) -> pd.DataFrame:
        """Public method to compute percentiles with error handling."""
        try:
            return self._compute_percentiles()
        except Exception as e:
            log.error(f"Error computing percentiles: {e}")
            raise