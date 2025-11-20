import pandas as pd
from lre_client.db.database_manager import  SQLiteDBManager
from lre_client.db.query_store import QueryStore
from lre_client.analytics.percentile_calculator import PercentileCalculator
from lre_client.utils.logger import get_logger

log = get_logger(__name__)


class LoadTestAnalyticsManager:
    """Analytics manager combining summary metrics and percentile computation."""

    def __init__(self, db_path: str, chunksize: int = 100_000):
        self.db_path = db_path
        self.chunksize = chunksize

    def _get_summary_df(self) -> pd.DataFrame:
        """Fetch summary metrics using optimized SQLiteDBManager."""
        log.info("Fetching summary metrics...")
        with SQLiteDBManager(self.db_path) as db:
            df_summary = db.query_single(QueryStore.SQL_TRANSACTION_SUMMARY)
        log.info(f"Fetched summary for {len(df_summary):,} transaction groups")
        return df_summary

    def _get_percentiles_df(self) -> pd.DataFrame:
        """Compute percentiles using PercentileCalculator."""
        log.info("Computing percentiles...")
        calculator = PercentileCalculator(self.db_path, self.chunksize)
        df_percentiles = calculator.compute_percentiles()
        log.info(f"Computed percentiles for {len(df_percentiles):,} transaction groups")
        return df_percentiles

    def run(self) -> pd.DataFrame:
        """Run full analytics workflow: summary + percentiles + merge."""
        df_summary = self._get_summary_df()
        df_percentiles = self._get_percentiles_df()

        log.info("Merging summary and percentile data...")
        df_final = df_summary.merge(
            df_percentiles,
            on=["Script_Name", "Transaction_Name"],
            how="left"
        )

        # Fill any missing percentiles with 0
        percentile_cols = ['p50', 'p90', 'p95', 'p99']
        df_final[percentile_cols] = df_final[percentile_cols].fillna(0.0)

        log.info(f"Final dataset contains {len(df_final):,} rows")
        return df_final