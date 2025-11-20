import pandas as pd
import numpy as np
from typing import Dict, Tuple
from lre_client.db.database_manager import  SQLiteDBManager
from lre_client.db.query_store import QueryStore

from lre_client.utils.logger import get_logger

log = get_logger(__name__)


class PercentileCalculator:
    """Memory-efficient, incremental weighted percentile calculator."""

    def __init__(self, db_path: str, chunk_size: int = 100_000):
        self.db_path = db_path
        self.chunk_size = chunk_size
        self.percentiles = [50, 90, 95, 99]

    @staticmethod
    def _weighted_percentile(data: np.ndarray, weights: np.ndarray, percentiles: list) -> np.ndarray:
        """Compute weighted percentiles efficiently with edge case handling."""
        if data.size == 0:
            return np.zeros(len(percentiles), dtype=float)

        if data.size == 1:
            return np.full(len(percentiles), float(data[0]), dtype=float)

        sorter = np.argsort(data)
        data_sorted = data[sorter]
        weights_sorted = weights[sorter]
        cum_weights = np.cumsum(weights_sorted)

        # Handle potential division by zero
        total_weight = cum_weights[-1]
        if total_weight <= 0:
            return np.zeros(len(percentiles), dtype=float)

        cum_weights_norm = cum_weights / total_weight * 100
        return np.interp(percentiles, cum_weights_norm, data_sorted)

    def compute_percentiles(self) -> pd.DataFrame:
        """Compute weighted percentiles incrementally with memory monitoring."""
        group_data: Dict[Tuple[str, str], Dict[str, np.ndarray]] = {}
        total_rows = 0
        chunk_count = 0

        with SQLiteDBManager(self.db_path, default_chunk_size=self.chunk_size) as db:
            for chunk in db.query(QueryStore.SQL_TRANSACTION_RESPONSE_TIMES):
                total_rows += len(chunk)
                chunk_count += 1

                # Filter invalid data
                chunk = chunk[(chunk["Response_Times"] > 0) & (chunk["Counts"] > 0)]
                if chunk.empty:
                    continue

                # Process each transaction group in the chunk
                for (script, txn), group in chunk.groupby(["Script_Name", "Transaction_Name"]):
                    key = (script, txn)
                    times = group["Response_Times"].to_numpy(dtype=float)
                    weights = group["Counts"].to_numpy(dtype=float)

                    if key not in group_data:
                        group_data[key] = {"times": times, "weights": weights}
                    else:
                        # Merge incrementally: concatenate arrays
                        group_data[key]["times"] = np.concatenate([group_data[key]["times"], times])
                        group_data[key]["weights"] = np.concatenate([group_data[key]["weights"], weights])

                # Optional: Log progress for very large datasets
                if chunk_count % 10 == 0:
                    log.debug(f"Processed {chunk_count} chunks, {len(group_data):,} active groups")

        log.info(f"Processed {total_rows:,} rows across {chunk_count} chunks")
        log.info(f"Computing percentiles for {len(group_data):,} transaction groups")

        # Compute weighted percentiles for each group
        results = []
        successful_calculations = 0

        for key, arrays in group_data.items():
            script, txn = key
            times_array = arrays["times"]
            weights_array = arrays["weights"]

            # Skip groups with insufficient data
            if times_array.size < 2:
                log.debug(f"Insufficient data for {script}/{txn}: {times_array.size} points")
                continue

            try:
                p_values = self._weighted_percentile(times_array, weights_array, self.percentiles)
                p50_val = float(p_values[0])
                p90_val = float(p_values[1])
                p95_val = float(p_values[2])
                p99_val = float(p_values[3])

                results.append({
                    "Script_Name": script,
                    "Transaction_Name": txn,
                    "p50": max(0.0, p50_val),
                    "p90": max(0.0, p90_val),
                    "p95": max(0.0, p95_val),
                    "p99": max(0.0, p99_val),
                })
                successful_calculations += 1
            except Exception as e:
                log.warning(f"Error computing percentiles for {script}/{txn}: {e}")
                # Optionally include failed groups with zeros
                results.append({
                    "Script_Name": script,
                    "Transaction_Name": txn,
                    "p50": 0.0,
                    "p90": 0.0,
                    "p95": 0.0,
                    "p99": 0.0,
                })

        log.info(f"Successfully computed percentiles for {successful_calculations:,} out of {len(group_data):,} groups")
        return pd.DataFrame(results)