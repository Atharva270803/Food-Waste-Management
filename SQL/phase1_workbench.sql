-- ============================================================
-- LOCAL FOOD WASTAGE MANAGEMENT SYSTEM
-- PHASE 1: DATABASE SETUP, SCHEMA & DATA LOADING
-- Run entirely in MySQL Workbench
-- Before running: Edit > Preferences > SQL Editor
--   Enable "Allow Loading Local Files" then reconnect
-- ============================================================

-- STEP 1: Create and select database
CREATE DATABASE IF NOT EXISTS food_wastage
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE food_wastage;

-- STEP 2: Enable local file loading
SET GLOBAL local_infile = 1;

-- STEP 3: Drop existing tables (safe re-run)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS food_listings;
DROP TABLE IF EXISTS providers;
DROP TABLE IF EXISTS receivers;
SET FOREIGN_KEY_CHECKS = 1;

-- STEP 4: Create tables

CREATE TABLE providers (
    Provider_ID INT          PRIMARY KEY,
    Name        VARCHAR(150) NOT NULL,
    Type        VARCHAR(50)  NOT NULL,
    Address     TEXT,
    City        VARCHAR(100) NOT NULL,
    Contact     VARCHAR(50)
);

CREATE TABLE receivers (
    Receiver_ID INT          PRIMARY KEY,
    Name        VARCHAR(150) NOT NULL,
    Type        VARCHAR(50)  NOT NULL,
    City        VARCHAR(100) NOT NULL,
    Contact     VARCHAR(50)
);

CREATE TABLE food_listings (
    Food_ID       INT          PRIMARY KEY,
    Food_Name     VARCHAR(100) NOT NULL,
    Quantity      INT          NOT NULL,
    Expiry_Date   DATE         NOT NULL,
    Provider_ID   INT          NOT NULL,
    Provider_Type VARCHAR(50)  NOT NULL,
    Location      VARCHAR(100) NOT NULL,
    Food_Type     VARCHAR(30)  NOT NULL,
    Meal_Type     VARCHAR(30)  NOT NULL,
    FOREIGN KEY (Provider_ID) REFERENCES providers(Provider_ID)
);

CREATE TABLE claims (
    Claim_ID    INT         PRIMARY KEY,
    Food_ID     INT         NOT NULL,
    Receiver_ID INT         NOT NULL,
    Status      VARCHAR(20) NOT NULL,
    Timestamp   DATETIME    NOT NULL,
    CONSTRAINT chk_status CHECK (Status IN ('Pending','Completed','Cancelled')),
    FOREIGN KEY (Food_ID)     REFERENCES food_listings(Food_ID),
    FOREIGN KEY (Receiver_ID) REFERENCES receivers(Receiver_ID)
);

-- STEP 5: Indexes
CREATE INDEX idx_food_provider   ON food_listings(Provider_ID);
CREATE INDEX idx_food_location   ON food_listings(Location);
CREATE INDEX idx_food_type       ON food_listings(Food_Type);
CREATE INDEX idx_food_meal       ON food_listings(Meal_Type);
CREATE INDEX idx_food_expiry     ON food_listings(Expiry_Date);
CREATE INDEX idx_claims_food     ON claims(Food_ID);
CREATE INDEX idx_claims_receiver ON claims(Receiver_ID);
CREATE INDEX idx_claims_status   ON claims(Status);
CREATE INDEX idx_provider_city   ON providers(City);
CREATE INDEX idx_receiver_city   ON receivers(City);

-- STEP 6: Load data
-- UPDATE PATHS BELOW to match your local folder before running

LOAD DATA LOCAL INFILE 'D:/Atharva/PROJECTS/labmentix/project 5 Food Management/providers_data.csv'
INTO TABLE providers
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Provider_ID, Name, Type, Address, City, Contact);

LOAD DATA LOCAL INFILE 'D:/Atharva/PROJECTS/labmentix/project 5 Food Management/receivers_data.csv'
INTO TABLE receivers
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Receiver_ID, Name, Type, City, Contact);

LOAD DATA LOCAL INFILE 'D:/Atharva/PROJECTS/labmentix/project 5 Food Management/food_listings_data.csv'
INTO TABLE food_listings
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Food_ID, Food_Name, Quantity, @Expiry_Date, Provider_ID,
 Provider_Type, Location, Food_Type, Meal_Type)
SET Expiry_Date = STR_TO_DATE(@Expiry_Date, '%m/%d/%Y');

LOAD DATA LOCAL INFILE 'D:/Atharva/PROJECTS/labmentix/project 5 Food Management/claims_data.csv'
INTO TABLE claims
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Claim_ID, Food_ID, Receiver_ID, Status, @Timestamp)
SET Timestamp = STR_TO_DATE(@Timestamp, '%m/%d/%Y %H:%i');

-- STEP 7: Verification
-- All counts should be 1000
SELECT COUNT(*) AS providers_count  FROM providers;
SELECT COUNT(*) AS receivers_count  FROM receivers;
SELECT COUNT(*) AS food_count       FROM food_listings;
SELECT COUNT(*) AS claims_count     FROM claims;

-- All orphan checks should return 0
SELECT COUNT(*) AS orphaned_food
FROM food_listings f
LEFT JOIN providers p ON f.Provider_ID = p.Provider_ID
WHERE p.Provider_ID IS NULL;

SELECT COUNT(*) AS orphaned_claims_food
FROM claims c
LEFT JOIN food_listings f ON c.Food_ID = f.Food_ID
WHERE f.Food_ID IS NULL;

SELECT COUNT(*) AS orphaned_claims_receiver
FROM claims c
LEFT JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
WHERE r.Receiver_ID IS NULL;

-- Sample rows
SELECT * FROM providers     LIMIT 3;
SELECT * FROM receivers     LIMIT 3;
SELECT * FROM food_listings LIMIT 3;
SELECT * FROM claims        LIMIT 3;
