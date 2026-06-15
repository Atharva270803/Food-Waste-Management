-- ============================================================
-- LOCAL FOOD WASTAGE MANAGEMENT SYSTEM
-- PHASE 3: 15 SQL ANALYSIS QUERIES
-- Run in MySQL Workbench
-- ============================================================

USE food_wastage;

-- ============================================================
-- QUERY 1: Total food listings by provider type
-- Shows which type of provider contributes most food
-- ============================================================
SELECT
    Provider_Type,
    COUNT(*)            AS total_listings,
    SUM(Quantity)       AS total_quantity,
    ROUND(AVG(Quantity), 2) AS avg_quantity_per_listing,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM food_listings), 2) AS pct_of_total
FROM food_listings
GROUP BY Provider_Type
ORDER BY total_quantity DESC;

-- ============================================================
-- QUERY 2: Top 10 most donated food items
-- Shows which foods appear most frequently in listings
-- ============================================================
SELECT
    Food_Name,
    COUNT(*)        AS times_listed,
    SUM(Quantity)   AS total_quantity_available,
    Food_Type,
    Meal_Type
FROM food_listings
GROUP BY Food_Name, Food_Type, Meal_Type
ORDER BY total_quantity_available DESC
LIMIT 10;

-- ============================================================
-- QUERY 3: Food availability by food type and meal type
-- Cross-tab of vegetarian/vegan/non-veg vs meal category
-- ============================================================
SELECT
    Food_Type,
    Meal_Type,
    COUNT(*)        AS listings,
    SUM(Quantity)   AS total_quantity,
    ROUND(AVG(Quantity), 2) AS avg_quantity
FROM food_listings
GROUP BY Food_Type, Meal_Type
ORDER BY Food_Type, Meal_Type;

-- ============================================================
-- QUERY 4: Claim status distribution
-- Overall breakdown of Pending / Completed / Cancelled claims
-- ============================================================
SELECT
    Status,
    COUNT(*) AS total_claims,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS percentage
FROM claims
GROUP BY Status
ORDER BY total_claims DESC;

-- ============================================================
-- QUERY 5: Claim completion rate by receiver type
-- Which receiver type converts the most claims to Completed?
-- ============================================================
SELECT
    r.Type AS receiver_type,
    COUNT(c.Claim_ID)                                               AS total_claims,
    SUM(CASE WHEN c.Status = 'Completed'  THEN 1 ELSE 0 END)       AS completed,
    SUM(CASE WHEN c.Status = 'Cancelled'  THEN 1 ELSE 0 END)       AS cancelled,
    SUM(CASE WHEN c.Status = 'Pending'    THEN 1 ELSE 0 END)       AS pending,
    ROUND(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(c.Claim_ID), 2)                          AS completion_rate_pct
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.Type
ORDER BY completion_rate_pct DESC;

-- ============================================================
-- QUERY 6: Top 10 most active providers (by food listed)
-- ============================================================
SELECT
    p.Provider_ID,
    p.Name          AS provider_name,
    p.Type          AS provider_type,
    p.City,
    COUNT(f.Food_ID)    AS total_listings,
    SUM(f.Quantity)     AS total_quantity_donated
FROM providers p
JOIN food_listings f ON p.Provider_ID = f.Provider_ID
GROUP BY p.Provider_ID, p.Name, p.Type, p.City
ORDER BY total_quantity_donated DESC
LIMIT 10;

-- ============================================================
-- QUERY 7: Top 10 most active receivers (by claims made)
-- ============================================================
SELECT
    r.Receiver_ID,
    r.Name          AS receiver_name,
    r.Type          AS receiver_type,
    r.City,
    COUNT(c.Claim_ID)                                               AS total_claims,
    SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END)        AS completed_claims,
    ROUND(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(c.Claim_ID), 2)                          AS success_rate_pct
FROM receivers r
JOIN claims c ON r.Receiver_ID = c.Receiver_ID
GROUP BY r.Receiver_ID, r.Name, r.Type, r.City
ORDER BY total_claims DESC
LIMIT 10;

-- ============================================================
-- QUERY 8: Food listings with no claims (unclaimed food)
-- These listings are at risk of going to waste
-- ============================================================
SELECT
    f.Food_ID,
    f.Food_Name,
    f.Quantity,
    f.Expiry_Date,
    f.Expiry_Status,
    f.Days_Until_Expiry,
    f.Food_Type,
    f.Meal_Type,
    p.Name          AS provider_name,
    p.City          AS provider_city
FROM food_listings f
JOIN providers p ON f.Provider_ID = p.Provider_ID
LEFT JOIN claims c ON f.Food_ID = c.Food_ID
WHERE c.Claim_ID IS NULL
ORDER BY f.Days_Until_Expiry ASC
LIMIT 20;

-- ============================================================
-- QUERY 9: Total quantity claimed vs available by food type
-- Shows how well each food type is being distributed
-- ============================================================
SELECT
    f.Food_Type,
    SUM(f.Quantity)                                                 AS total_available,
    COUNT(DISTINCT f.Food_ID)                                       AS total_listings,
    COUNT(DISTINCT c.Claim_ID)                                      AS total_claims,
    SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END)        AS completed_claims,
    ROUND(COUNT(DISTINCT c.Claim_ID) * 100.0
          / COUNT(DISTINCT f.Food_ID), 2)                          AS claims_per_listing
FROM food_listings f
LEFT JOIN claims c ON f.Food_ID = c.Food_ID
GROUP BY f.Food_Type
ORDER BY total_available DESC;

-- ============================================================
-- QUERY 10: Daily claim activity trend
-- Shows claim volume by day of week
-- ============================================================
SELECT
    Claim_Day                                                       AS day_of_week,
    COUNT(*)                                                        AS total_claims,
    SUM(CASE WHEN Status = 'Completed' THEN 1 ELSE 0 END)          AS completed,
    SUM(CASE WHEN Status = 'Cancelled' THEN 1 ELSE 0 END)          AS cancelled,
    SUM(CASE WHEN Status = 'Pending'   THEN 1 ELSE 0 END)          AS pending,
    ROUND(SUM(CASE WHEN Status = 'Completed' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)                                   AS completion_rate_pct
FROM claims
GROUP BY Claim_Day
ORDER BY total_claims DESC;

-- ============================================================
-- QUERY 11: Expiry urgency vs claim status
-- Are urgent/critical food items being claimed in time?
-- ============================================================
SELECT
    f.Expiry_Status,
    COUNT(DISTINCT f.Food_ID)                                       AS food_listings,
    COUNT(c.Claim_ID)                                               AS total_claims,
    SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END)        AS completed,
    SUM(CASE WHEN c.Status = 'Cancelled' THEN 1 ELSE 0 END)        AS cancelled,
    SUM(CASE WHEN c.Status = 'Pending'   THEN 1 ELSE 0 END)        AS pending,
    ROUND(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END)
          * 100.0 / NULLIF(COUNT(c.Claim_ID), 0), 2)              AS completion_rate_pct
FROM food_listings f
LEFT JOIN claims c ON f.Food_ID = c.Food_ID
GROUP BY f.Expiry_Status
ORDER BY f.Expiry_Status;

-- ============================================================
-- QUERY 12: Provider performance scorecard
-- Which providers have the highest claim rate on their food?
-- ============================================================
SELECT
    p.Name          AS provider_name,
    p.Type          AS provider_type,
    COUNT(DISTINCT f.Food_ID)                                       AS food_listings,
    SUM(f.Quantity)                                                 AS total_quantity,
    COUNT(DISTINCT c.Claim_ID)                                      AS claims_received,
    SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END)        AS completed_claims,
    ROUND(COUNT(DISTINCT c.Claim_ID) * 100.0
          / NULLIF(COUNT(DISTINCT f.Food_ID), 0), 2)               AS claim_rate_pct
FROM providers p
JOIN food_listings f ON p.Provider_ID = f.Provider_ID
LEFT JOIN claims c ON f.Food_ID = c.Food_ID
GROUP BY p.Provider_ID, p.Name, p.Type
ORDER BY claim_rate_pct DESC
LIMIT 15;

-- ============================================================
-- QUERY 13: Food distribution by location (top 15 cities)
-- Which locations have the most food available?
-- ============================================================
SELECT
    f.Location,
    COUNT(DISTINCT f.Food_ID)                                       AS total_listings,
    SUM(f.Quantity)                                                 AS total_quantity,
    COUNT(DISTINCT c.Claim_ID)                                      AS total_claims,
    SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END)        AS completed_claims,
    ROUND(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END)
          * 100.0 / NULLIF(COUNT(DISTINCT c.Claim_ID), 0), 2)     AS completion_rate_pct
FROM food_listings f
LEFT JOIN claims c ON f.Food_ID = c.Food_ID
GROUP BY f.Location
ORDER BY total_quantity DESC
LIMIT 15;

-- ============================================================
-- QUERY 14: Meal type demand analysis
-- Which meal types receive the most claims?
-- ============================================================
SELECT
    f.Meal_Type,
    COUNT(DISTINCT f.Food_ID)                                       AS food_listings,
    SUM(f.Quantity)                                                 AS total_quantity,
    COUNT(c.Claim_ID)                                               AS total_claims,
    SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END)        AS completed_claims,
    ROUND(COUNT(c.Claim_ID) * 100.0
          / NULLIF(COUNT(DISTINCT f.Food_ID), 0), 2)               AS claims_per_listing,
    ROUND(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END)
          * 100.0 / NULLIF(COUNT(c.Claim_ID), 0), 2)              AS completion_rate_pct
FROM food_listings f
LEFT JOIN claims c ON f.Food_ID = c.Food_ID
GROUP BY f.Meal_Type
ORDER BY total_claims DESC;

-- ============================================================
-- QUERY 15: End-to-end food waste risk report
-- Combines provider, food, and claim data to identify
-- high-quantity unclaimed food at risk of expiring
-- ============================================================
SELECT
    f.Food_ID,
    f.Food_Name,
    f.Quantity,
    f.Expiry_Date,
    f.Days_Until_Expiry,
    f.Expiry_Status,
    f.Food_Type,
    f.Meal_Type,
    p.Name          AS provider_name,
    p.Type          AS provider_type,
    p.City          AS provider_city,
    COUNT(c.Claim_ID)                                               AS total_claims,
    SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END)        AS completed_claims,
    SUM(CASE WHEN c.Status = 'Pending'   THEN 1 ELSE 0 END)        AS pending_claims,
    CASE
        WHEN COUNT(c.Claim_ID) = 0                                  THEN 'No Claims — High Risk'
        WHEN SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) > 0 THEN 'Claimed — Safe'
        WHEN SUM(CASE WHEN c.Status = 'Pending'   THEN 1 ELSE 0 END) > 0 THEN 'Pending — Monitor'
        ELSE                                                             'Cancelled Only — At Risk'
    END AS waste_risk_label
FROM food_listings f
JOIN providers p ON f.Provider_ID = p.Provider_ID
LEFT JOIN claims c ON f.Food_ID = c.Food_ID
GROUP BY
    f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date,
    f.Days_Until_Expiry, f.Expiry_Status, f.Food_Type, f.Meal_Type,
    p.Name, p.Type, p.City
ORDER BY f.Quantity DESC, f.Days_Until_Expiry ASC
LIMIT 20;

