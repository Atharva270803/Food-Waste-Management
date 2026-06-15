-- ============================================================
-- LOCAL FOOD WASTAGE MANAGEMENT SYSTEM
-- PHASE 2: DATA CLEANING & VALIDATION
-- Run entirely in MySQL Workbench
-- ============================================================

USE food_wastage;

-- ============================================================
-- SECTION 1: UNDERSTAND THE DATA BEFORE TOUCHING ANYTHING
-- ============================================================

-- 1a. Check date ranges
SELECT
    MIN(Expiry_Date) AS earliest_expiry,
    MAX(Expiry_Date) AS latest_expiry,
    COUNT(*) AS total_food_listings
FROM food_listings;

SELECT
    MIN(Timestamp) AS earliest_claim,
    MAX(Timestamp) AS latest_claim,
    COUNT(*) AS total_claims
FROM claims;

-- 1b. Check for NULL values across all tables
SELECT
    SUM(CASE WHEN Provider_ID IS NULL THEN 1 ELSE 0 END) AS null_provider_id,
    SUM(CASE WHEN Name       IS NULL THEN 1 ELSE 0 END) AS null_name,
    SUM(CASE WHEN Type       IS NULL THEN 1 ELSE 0 END) AS null_type,
    SUM(CASE WHEN City       IS NULL THEN 1 ELSE 0 END) AS null_city,
    SUM(CASE WHEN Contact    IS NULL THEN 1 ELSE 0 END) AS null_contact
FROM providers;

SELECT
    SUM(CASE WHEN Receiver_ID IS NULL THEN 1 ELSE 0 END) AS null_receiver_id,
    SUM(CASE WHEN Name        IS NULL THEN 1 ELSE 0 END) AS null_name,
    SUM(CASE WHEN Type        IS NULL THEN 1 ELSE 0 END) AS null_type,
    SUM(CASE WHEN City        IS NULL THEN 1 ELSE 0 END) AS null_city,
    SUM(CASE WHEN Contact     IS NULL THEN 1 ELSE 0 END) AS null_contact
FROM receivers;

SELECT
    SUM(CASE WHEN Food_ID       IS NULL THEN 1 ELSE 0 END) AS null_food_id,
    SUM(CASE WHEN Food_Name     IS NULL THEN 1 ELSE 0 END) AS null_food_name,
    SUM(CASE WHEN Quantity      IS NULL THEN 1 ELSE 0 END) AS null_quantity,
    SUM(CASE WHEN Expiry_Date   IS NULL THEN 1 ELSE 0 END) AS null_expiry,
    SUM(CASE WHEN Provider_ID   IS NULL THEN 1 ELSE 0 END) AS null_provider_id,
    SUM(CASE WHEN Location      IS NULL THEN 1 ELSE 0 END) AS null_location,
    SUM(CASE WHEN Food_Type     IS NULL THEN 1 ELSE 0 END) AS null_food_type,
    SUM(CASE WHEN Meal_Type     IS NULL THEN 1 ELSE 0 END) AS null_meal_type
FROM food_listings;

SELECT
    SUM(CASE WHEN Claim_ID    IS NULL THEN 1 ELSE 0 END) AS null_claim_id,
    SUM(CASE WHEN Food_ID     IS NULL THEN 1 ELSE 0 END) AS null_food_id,
    SUM(CASE WHEN Receiver_ID IS NULL THEN 1 ELSE 0 END) AS null_receiver_id,
    SUM(CASE WHEN Status      IS NULL THEN 1 ELSE 0 END) AS null_status,
    SUM(CASE WHEN Timestamp   IS NULL THEN 1 ELSE 0 END) AS null_timestamp
FROM claims;

-- 1c. Check for duplicate primary keys
SELECT COUNT(*) AS total, COUNT(DISTINCT Provider_ID) AS unique_ids,
       COUNT(*) - COUNT(DISTINCT Provider_ID) AS duplicates
FROM providers;

SELECT COUNT(*) AS total, COUNT(DISTINCT Receiver_ID) AS unique_ids,
       COUNT(*) - COUNT(DISTINCT Receiver_ID) AS duplicates
FROM receivers;

SELECT COUNT(*) AS total, COUNT(DISTINCT Food_ID) AS unique_ids,
       COUNT(*) - COUNT(DISTINCT Food_ID) AS duplicates
FROM food_listings;

SELECT COUNT(*) AS total, COUNT(DISTINCT Claim_ID) AS unique_ids,
       COUNT(*) - COUNT(DISTINCT Claim_ID) AS duplicates
FROM claims;

-- 1d. Check quantity range (should be 1-50, no negatives or zeros)
SELECT
    MIN(Quantity) AS min_qty,
    MAX(Quantity) AS max_qty,
    AVG(Quantity) AS avg_qty,
    SUM(CASE WHEN Quantity <= 0 THEN 1 ELSE 0 END) AS zero_or_negative
FROM food_listings;

-- 1e. Check status values (should only be Pending/Completed/Cancelled)
SELECT Status, COUNT(*) AS count
FROM claims
GROUP BY Status;

-- 1f. Check food type and meal type values
SELECT Food_Type, COUNT(*) AS count FROM food_listings GROUP BY Food_Type;
SELECT Meal_Type, COUNT(*) AS count FROM food_listings GROUP BY Meal_Type;

-- 1g. Check provider type consistency between tables
SELECT 'providers table'    AS source, Type, COUNT(*) AS count FROM providers     GROUP BY Type
UNION ALL
SELECT 'food_listings table' AS source, Provider_Type, COUNT(*) FROM food_listings GROUP BY Provider_Type;

-- 1h. Food items with multiple claims (valid but worth knowing)
SELECT
    Food_ID,
    COUNT(*) AS claim_count
FROM claims
GROUP BY Food_ID
HAVING claim_count > 1
ORDER BY claim_count DESC
LIMIT 10;

-- 1i. Claim status breakdown by receiver type
SELECT
    r.Type AS receiver_type,
    c.Status,
    COUNT(*) AS count
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.Type, c.Status
ORDER BY r.Type, c.Status;

-- ============================================================
-- SECTION 2: REFERENTIAL INTEGRITY CHECKS
-- All should return 0
-- ============================================================

-- 2a. Food listings with invalid Provider_ID
SELECT COUNT(*) AS orphaned_food_listings
FROM food_listings f
LEFT JOIN providers p ON f.Provider_ID = p.Provider_ID
WHERE p.Provider_ID IS NULL;

-- 2b. Claims with invalid Food_ID
SELECT COUNT(*) AS orphaned_claims_food
FROM claims c
LEFT JOIN food_listings f ON c.Food_ID = f.Food_ID
WHERE f.Food_ID IS NULL;

-- 2c. Claims with invalid Receiver_ID
SELECT COUNT(*) AS orphaned_claims_receiver
FROM claims c
LEFT JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
WHERE r.Receiver_ID IS NULL;

-- ============================================================
-- SECTION 3: ADD COMPUTED COLUMNS FOR ANALYSIS
-- ============================================================

SET SQL_SAFE_UPDATES = 0;

-- 3a. Add Days_Until_Expiry column to food_listings
--     Useful for identifying food expiring soon
ALTER TABLE food_listings ADD COLUMN Days_Until_Expiry INT;

UPDATE food_listings
SET Days_Until_Expiry = DATEDIFF(Expiry_Date, '2025-03-01');
-- Using 2025-03-01 as reference (earliest claim date = dataset start)

-- 3b. Add Expiry_Status column — categorises urgency
ALTER TABLE food_listings ADD COLUMN Expiry_Status VARCHAR(20);

UPDATE food_listings
SET Expiry_Status = CASE
    WHEN Days_Until_Expiry <= 5  THEN 'Critical'
    WHEN Days_Until_Expiry <= 10 THEN 'Urgent'
    WHEN Days_Until_Expiry <= 20 THEN 'Normal'
    ELSE                              'Fresh'
END;

-- 3c. Add Claim_Month and Claim_Day columns to claims
--     Makes temporal analysis in Phase 3 much cleaner
ALTER TABLE claims ADD COLUMN Claim_Month TINYINT;
ALTER TABLE claims ADD COLUMN Claim_Day   VARCHAR(10);

UPDATE claims
SET
    Claim_Month = MONTH(Timestamp),
    Claim_Day   = DAYNAME(Timestamp);

SET SQL_SAFE_UPDATES = 1;

-- ============================================================
-- SECTION 4: FINAL VERIFICATION
-- ============================================================

-- 4a. Confirm new columns populated correctly
SELECT
    Expiry_Status,
    COUNT(*) AS food_count,
    MIN(Days_Until_Expiry) AS min_days,
    MAX(Days_Until_Expiry) AS max_days
FROM food_listings
GROUP BY Expiry_Status
ORDER BY min_days;

-- 4b. Confirm claim temporal columns
SELECT Claim_Month, Claim_Day, COUNT(*) AS claims
FROM claims
GROUP BY Claim_Month, Claim_Day
ORDER BY Claim_Month, claims DESC
LIMIT 10;

-- 4c. Final row counts — should all still be 1000
SELECT
    (SELECT COUNT(*) FROM providers)     AS providers,
    (SELECT COUNT(*) FROM receivers)     AS receivers,
    (SELECT COUNT(*) FROM food_listings) AS food_listings,
    (SELECT COUNT(*) FROM claims)        AS claims;

-- 4d. Show updated food_listings structure
DESCRIBE food_listings;
DESCRIBE claims;

-- ============================================================
-- CLEANING SUMMARY
-- NULLs found:           0 across all tables
-- Duplicate PKs:         0 across all tables
-- Negative quantities:   0
-- Invalid status values: 0
-- Orphaned foreign keys: 0
-- New columns added:
--   food_listings: Days_Until_Expiry, Expiry_Status
--   claims:        Claim_Month, Claim_Day
-- ============================================================
