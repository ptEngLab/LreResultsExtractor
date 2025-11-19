# query_store.py

class QueryStore:
    """
    Central repository for all SQL queries used for reporting from LRE SQLite DBs.
    """
    run_metadata = """
            SELECT run_id, scenario_name, start_time, end_time, duration
            FROM Run
        """

    transaction_summary= """
            SELECT
                TransactionName,
                COUNT(*) AS TotalSamples,
                AVG(Duration) AS AvgDuration,
                MIN(Duration) AS MinDuration,
                MAX(Duration) AS MaxDuration,
                SUM(CASE WHEN Passed = 1 THEN 1 ELSE 0 END) AS PassedCount,
                SUM(CASE WHEN Passed = 0 THEN 1 ELSE 0 END) AS FailedCount
            FROM Transactions
            GROUP BY TransactionName
            ORDER BY TransactionName
        """


