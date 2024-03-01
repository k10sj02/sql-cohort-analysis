-- Techniques used include Database Creation, Data Cleaning, Common Table Expressions (CTEs), 
-- Temporary Tables Creation, Window Functions (ROW_NUMBER()), JOINs on Temp Tables, 
-- Data Transformation and Calculation, PIVOT Function, Data Presentation and Reporting

-- create database from CSV file

USE master;
GO

IF NOT EXISTS (
      SELECT name
      FROM sys.databases
      WHERE name = N'TutorialDB'
      )
   CREATE DATABASE [OnlineCommerceDB];
GO

IF SERVERPROPERTY('ProductVersion') > '12'
   ALTER DATABASE [OnlineCommerceDB] SET QUERY_STORE = ON;
GO

-- Cleaning Data

SELECT COUNT(*) AS records
FROM [OnlineCommerceDB].[dbo].[Online Retail]

-- We have 541,909 rows.

SELECT *
FROM OnlineCommerceDB.dbo.[Online Retail]
WHERE Quantity < 0;

-- Items with negative quantities may include returns

SELECT COUNT(*) AS tuples
FROM OnlineCommerceDB.dbo.[Online Retail]
WHERE CustomerID IS NULL

-- 135080 records have null/no customerID

SELECT COUNT(*) AS tuples
FROM OnlineCommerceDB.dbo.[Online Retail]
WHERE CustomerID IS NOT NULL

-- RECAP:
-- We have 541,909 rows.
-- 135080 records have null/no customerID
-- 406829 records have a customer IDs. The null and non-null records are equal to the total number of rows. Phew! 

;WITH online_retail AS
(
   SELECT 
      InvoiceNo, 
      StockCode, 
      [Description], 
      Quantity, 
      InvoiceDate, 
      UnitPrice, 
      CustomerID, 
      Country
   FROM OnlineCommerceDB.dbo.[Online Retail]
   WHERE CustomerID IS NOT NULL
)
, quantity_unit_price AS
(
   -- This gives us 397884 rows. We have reduced the dataset by 2% by excluding negative quantity and unit price attributes.
   SELECT *
   FROM online_retail
   WHERE Quantity > 0 AND UnitPrice > 0
)
, dup_check AS
(
-- duplicate check
SELECT *, 
      ROW_NUMBER() OVER (PARTITION BY InvoiceNo, StockCode, Quantity ORDER BY InvoiceDate) AS dupflag
FROM quantity_unit_price
)
-- 392669 rows in cleaned dataset.
-- 5215 duplicate rows.
SELECT * 
INTO #online_retail_main
FROM dup_check
WHERE dupflag = 1

-- CLEAN DATA 
-- Begin Cohort Analysis
SELECT *
FROM #online_retail_main;

-- METRICS NEEDED TO CONDUCT *TIME-BASED* COHORT ANALYSIS:
-- You also have size-based and segment-based analyses.
   -- Unique Identifier (CustomerID)
   -- Initital Start Date
   -- Revenue Data

SELECT
   CustomerID,
   MIN(InvoiceDate) AS first_purchase_date,
   DATEFROMPARTS(YEAR(MIN(InvoiceDate)), MONTH(MIN(InvoiceDate)), 1) AS Cohort_Date
INTO #Cohort
FROM #online_retail_main
GROUP BY CustomerID;

SELECT *
FROM #Cohort;

-- Create Cohort Index 
   -- Cohort Index describes the number of months that have passed since the customer's first purchase. 

DROP TABLE IF EXISTS  #cohort_retention
GO
SELECT
   mmm.*,
   cohort_index = YEAR_DIFF * 12 + MONTH_DIFF + 1
INTO #cohort_retention
FROM
   (
      SELECT
         mm.*,
         YEAR_DIFF = invoice_year - cohort_year,
         MONTH_DIFF = invoice_month - cohort_month
FROM
         (
            SELECT
                  m.*,
                  c.Cohort_Date,
                  YEAR(m.InvoiceDate) AS invoice_year,          -- [we include invoice dates to determine each month that the customer 
                  MONTH(m.InvoiceDate) AS invoice_month,        -- remains in our cohort].
                  YEAR(c.Cohort_Date) AS cohort_year,
                  MONTH(c.Cohort_Date) AS cohort_month
            FROM #online_retail_main m
            LEFT JOIN #Cohort c ON m.CustomerID = c.CustomerID
            --WHERE c.CustomerID = '14733'
         ) mm
) mmm

SELECT *
FROM #cohort_retention

-- check unique indexes in dataset and use them in for loop above
SELECT DISTINCT cohort_index FROM #cohort_retention;

-- Pivot Data to see the cohort table 

SELECT *
INTO #cohort_pivot
FROM
   (
   SELECT DISTINCT
            CustomerID,
            Cohort_Date,
            cohort_index
   FROM #cohort_retention
) tbl
PIVOT(
   COUNT(CustomerID)
   for cohort_index IN
   (
      [1],
      [2],
      [3],
      [4],
      [5],
      [6],
      [7],
      [8],
      [9],
      [10],
      [11],
      [12],
      [13]
   )
) AS pivot_table;

-- see pivot table by absolute numbers
SELECT *
FROM #cohort_pivot
ORDER BY Cohort_Date;

-- see pivot table by percentages 

SELECT Cohort_Date,
      1.0 * [1]/[1] * 100 AS [1],
      1.0 * [2]/[1] * 100 AS [2],
      1.0 * [3]/[1] * 100 AS [3],
      1.0 * [4]/[1] * 100 AS [4],
      1.0 * [5]/[1] * 100 AS [5],
      1.0 * [6]/[1] * 100 AS [6],
      1.0 * [7]/[1] * 100 AS [7],
      1.0 * [8]/[1] * 100 AS [8],
      1.0 * [9]/[1] * 100 AS [9],
      1.0 * [10]/[1] * 100 AS [10],
      1.0 * [11]/[1] * 100 AS [11],
      1.0 * [12]/[1] * 100 AS [12],
      1.0 * [13]/[1] * 100 AS [13]
FROM #cohort_pivot
ORDER BY Cohort_Date;


