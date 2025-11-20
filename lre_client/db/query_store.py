# query_store.py

class QueryStore:
    """
    Central repository for all SQL queries used for reporting from LRE SQLite DBs.
    """
    SQL_TRANSACTION_RESPONSE_TIMES = """
    SELECT
        vg."Group Name" AS Script_Name,
        EMAP."Event Name" AS Transaction_Name,
        EM.Value - COALESCE(EM."Think Time", 0) AS Response_Times,
        EM.Acount AS Counts
    FROM Event_meter EM
    JOIN Script s 
        ON EM."Script ID" = s."Script ID"
    JOIN Event_map EMAP 
        ON EM."Event Name" = EMAP."Event Name"
        AND EMAP."Event Type" = 'Transaction'
    JOIN TransactionEndStatus TES 
        ON EM.Status1 = TES.Status1
    JOIN VuserGroup vg 
        ON EM."Group ID" = vg."Group ID"
    WHERE TES."Transaction End Status" = 'Pass'
      AND EM.Value - COALESCE(EM."Think Time", 0) IS NOT NULL
      AND EM.Value - COALESCE(EM."Think Time", 0) > 0
      AND EM.Acount > 0
    ;
    """


    SQL_TRANSACTION_SUMMARY = """
    SELECT
        vg."Group Name" AS Script_Name,
        EMAP."Event Name" AS Transaction_Name,
        CAST(SUM(EM.Acount) AS INTEGER) AS Transaction_Count,
    
        ROUND(MIN(CASE WHEN TES."Transaction End Status" = 'Pass'
                       THEN EM.Value - COALESCE(EM."Think Time", 0) END), 3) AS Minimum,
    
        ROUND(SUM(CASE WHEN TES."Transaction End Status" = 'Pass'
                       THEN (EM.Value - COALESCE(EM."Think Time", 0)) * EM.Acount ELSE 0 END) /
              NULLIF(SUM(CASE WHEN TES."Transaction End Status" = 'Pass'
                       THEN EM.Acount ELSE 0 END), 0), 3) AS Average,
    
        ROUND(MAX(CASE WHEN TES."Transaction End Status" = 'Pass'
                       THEN EM.Value - COALESCE(EM."Think Time", 0) END), 3) AS Maximum,
    
        ROUND(
            CASE WHEN SUM(CASE WHEN TES."Transaction End Status" = 'Pass' THEN EM.Acount ELSE 0 END) > 0 THEN
                SQRT(
                    (
                        SUM(CASE WHEN TES."Transaction End Status" = 'Pass'
                                 THEN EM.Acount * POWER(EM.Value - COALESCE(EM."Think Time", 0), 2)
                                 ELSE 0 END) /
                        SUM(CASE WHEN TES."Transaction End Status" = 'Pass' THEN EM.Acount ELSE 0 END)
                    ) -
                    POWER(
                        SUM(CASE WHEN TES."Transaction End Status" = 'Pass'
                                 THEN (EM.Value - COALESCE(EM."Think Time", 0)) * EM.Acount
                                 ELSE 0 END) /
                        SUM(CASE WHEN TES."Transaction End Status" = 'Pass'
                                 THEN EM.Acount ELSE 0 END),
                    2)
                )
            ELSE 0 END,
        3) AS Std_Deviation,
    
        CAST(SUM(CASE WHEN TES."Transaction End Status" = 'Pass' THEN EM.Acount ELSE 0 END) AS INTEGER) AS Pass,
        CAST(SUM(CASE WHEN TES."Transaction End Status" = 'Fail' THEN EM.Acount ELSE 0 END) AS INTEGER) AS Fail
    
    FROM Event_meter EM
    JOIN Script s ON EM."Script ID" = s."Script ID"
    JOIN Event_map EMAP ON EM."Event Name" = EMAP."Event Name" AND EMAP."Event Type" = 'Transaction'
    JOIN TransactionEndStatus TES ON EM.Status1 = TES.Status1
    JOIN VuserGroup vg ON EM."Group ID" = vg."Group ID"
    
    GROUP BY vg."Group Name", EMAP."Event Name"
    ORDER BY vg."Group Name", EMAP."Event Name";
    """