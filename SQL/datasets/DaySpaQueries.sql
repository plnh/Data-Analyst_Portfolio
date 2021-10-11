SELECT * 
fROM DaySpaRollup
order by CustomerID;

SELECT * 
fROM DaySpaVisit
order by CustomerVisitStart;


/* MAXIMUM OVERLAP */
Drop TABLE IF EXISTS #StartStopOrder;

/*Step 1 CTE startstoppoint */
WITH #StartStopPoints AS ( 
SELECT
-- This section focuses on entrances:  CustomerVisitStart
	dsv.CustomerVisitStart AS TimeUTC,
	1 AS EntryCount,
    -- Get a unique, ascending row number
	Row_number() OVER (
      -- Ordered by the customer visit start time
      ORDER BY dsv.CustomerVisitStart
    ) AS StartOrdinal
FROM DaySpaVisit dsv
UNION ALL
-- This section focuses on departures:  CustomerVisitEnd
SELECT
	dsv.CustomerVisitEnd AS TimeUTC,
	-1 AS EntryCount,
	NULL AS StartOrdinal
FROM DaySpaVisit dsv)  
/* Step 2 CTE #StartStopOrder*/
SELECT 
   s.TimeUTC,   
   s.EntryCount,    
   s.StartOrdinal,    
   ROW_NUMBER() OVER (ORDER BY s.TimeUTC, s.StartOrdinal) AS StartOrEndOrdinal
INTO #StartStopOrder
FROM #StartStopPoints s ;

SELECT MAX(2 * s.StartOrdinal - s.StartOrEndOrdinal) AS MaxConcurrentVisitors
FROM #StartStopOrder s
WHERE s.EntryCount = 1


/*FRAUD ANALYSIS */
Drop TABLE IF EXISTS #StartStopOrder;
/*Step 1 of the fraud analysis */
WITH #StartStopPoints AS ( 
SELECT
-- This section focuses on entrances:  CustomerVisitStart
	dsv.CustomerID,
	dsv.CustomerVisitStart AS TimeUTC,
	1 AS EntryCount,
    -- We want to know each customer's entrance stream
    -- Get a unique, ascending row number
	Row_number() OVER (
      -- Break this out by customer ID
      PARTITION BY dsv.CustomerID
      -- Ordered by the customer visit start date
      ORDER BY dsv.CustomerVisitStart
    ) AS StartOrdinal
FROM dbo.DaySpaVisit dsv
UNION ALL
-- This section focuses on departures:  CustomerVisitEnd
SELECT
	dsv.CustomerID,
	dsv.CustomerVisitEnd AS TimeUTC,
	-1 AS EntryCount,
	NULL AS StartOrdinal
FROM dbo.DaySpaVisit dsv)  

/* Step 2 */
SELECT s.*,
    -- Build a stream of all check-in and check-out events
	ROW_NUMBER() OVER (
      -- Break this out by customer ID
      PARTITION BY s.CustomerID
      -- Order by event time and then the start ordinal
      -- value (in case of exact time matches)
      ORDER BY s.TimeUTC, s.StartOrdinal
    ) AS StartOrEndOrdinal
INTO #StartStopOrder
FROM #StartStopPoints s ;

/* Complete the fraud analysis */
SELECT
	s.CustomerID,
	MAX(2 * s.StartOrdinal - s.StartOrEndOrdinal) AS MaxConcurrentCustomerVisits
INTO #fraud_list
FROM #StartStopOrder s
WHERE s.EntryCount = 1
GROUP BY s.CustomerID
-- The difference between 2 * start ordinal and the start/end
-- ordinal represents the number of concurrent visits
HAVING MAX(2 * s.StartOrdinal - s.StartOrEndOrdinal) > 2
-- Sort by the largest number of max concurrent customer visits
ORDER BY MaxConcurrentCustomerVisits desc;

/* Maximum overlap exluding fraud */
Drop TABLE IF EXISTS new_list;
--Creat new table without clients commited fraud--
SELECT *
INTO new_list
FROM DaySpaVisit
where CustomerID not in ( select CustomerID from #fraud_list); 


Drop TABLE IF EXISTS #StartStopOrder;

/*Step 1 CTE startstoppoint */
WITH #StartStopPoints AS ( 
SELECT
-- This section focuses on entrances:  CustomerVisitStart
	dsv.CustomerVisitStart AS TimeUTC,
	1 AS EntryCount,
    -- We want to know each customer's entrance stream
    -- Get a unique, ascending row number
	Row_number() OVER (
      -- Ordered by the customer visit start time
      ORDER BY dsv.CustomerVisitStart
    ) AS StartOrdinal
FROM new_list dsv
UNION ALL
-- This section focuses on departures:  CustomerVisitEnd
SELECT
	dsv.CustomerVisitEnd AS TimeUTC,
	-1 AS EntryCount,
	NULL AS StartOrdinal
FROM new_list dsv)  
/* Step 2 CTE #StartStopOrder*/
SELECT 
   s.TimeUTC,   
   s.EntryCount,    
   s.StartOrdinal,    
   ROW_NUMBER() OVER (ORDER BY s.TimeUTC, s.StartOrdinal) AS StartOrEndOrdinal
INTO #StartStopOrder
FROM #StartStopPoints s ;

SELECT MAX(2 * s.StartOrdinal - s.StartOrEndOrdinal) AS MaxConcurrentVisitors
FROM #StartStopOrder s
WHERE s.EntryCount = 1