-- ============================================================================
-- SCHOOL BUS ROUTE AND STUDENT TRANSPORT MANAGEMENT SYSTEM
-- SCRIPT: 06_queries.sql
-- PURPOSE: Academic SQL demonstration suite (CRUD, Joins, Aggregations, Subqueries)
-- DBMS TARGET: MySQL 8.0+ / MariaDB
-- ============================================================================

USE school_transport_db;

-- ============================================================================
-- CATEGORY 1: BASIC CRUD & PROJECTION QUERIES
-- ============================================================================

-- Q1.1: Retrieve all active buses with capacity above 25
SELECT Bus_ID, Bus_Number, Registration_Number, Capacity, Bus_Model, Status
FROM BUS
WHERE Status = 'Active' AND Capacity > 25
ORDER BY Capacity DESC;

-- Q1.2: Find drivers with 10 or more years of experience
SELECT Driver_ID, Driver_Name, Phone_Number, License_Number, Experience
FROM DRIVER
WHERE Experience >= 10
ORDER BY Experience DESC;

-- Q1.3: Update driver contact number
UPDATE DRIVER
SET Phone_Number = '9123456799'
WHERE Driver_ID = 204;

-- Q1.4: Update bus status during scheduled maintenance
UPDATE BUS
SET Status = 'Maintenance'
WHERE Bus_ID = 304;

-- Revert back to active for testing
UPDATE BUS
SET Status = 'Active'
WHERE Bus_ID = 304;


-- ============================================================================
-- CATEGORY 2: MULTI-TABLE JOINS (INNER, LEFT, MULTI-WAY)
-- ============================================================================

-- Q2.1: 7-Table Full Transport Manifest (Student, Parent, Bus, Driver, Route, Stop)
SELECT 
    s.Student_ID,
    s.Student_Name,
    s.Class,
    s.Section,
    p.Parent_Name,
    p.Phone_Number AS Emergency_Contact,
    b.Bus_Number,
    d.Driver_Name,
    d.Phone_Number AS Driver_Contact,
    r.Route_Name,
    bs.Stop_Name,
    bs.Stop_Order
FROM TRANSPORT_ASSIGNMENT ta
INNER JOIN STUDENT s ON ta.Student_ID = s.Student_ID
INNER JOIN PARENT p ON s.Parent_ID = p.Parent_ID
INNER JOIN BUS b ON ta.Bus_ID = b.Bus_ID
INNER JOIN DRIVER d ON b.Driver_ID = d.Driver_ID
INNER JOIN ROUTE r ON ta.Route_ID = r.Route_ID
INNER JOIN BUS_STOP bs ON ta.Stop_ID = bs.Stop_ID
ORDER BY r.Route_Name, bs.Stop_Order, s.Student_Name;

-- Q2.2: Left Join - Find students who do NOT have any transport assignment
SELECT 
    s.Student_ID,
    s.Student_Name,
    s.Class,
    s.Section,
    p.Parent_Name,
    p.Phone_Number
FROM STUDENT s
JOIN PARENT p ON s.Parent_ID = p.Parent_ID
LEFT JOIN TRANSPORT_ASSIGNMENT ta ON s.Student_ID = ta.Student_ID
WHERE ta.Assignment_ID IS NULL;

-- Q2.3: Bus to Driver 1:1 Mapping with Vehicle Details
SELECT 
    b.Bus_Number,
    b.Registration_Number,
    b.Bus_Model,
    b.Capacity,
    d.Driver_Name,
    d.License_Number,
    d.Experience AS Driver_Experience
FROM BUS b
INNER JOIN DRIVER d ON b.Driver_ID = d.Driver_ID;


-- ============================================================================
-- CATEGORY 3: AGGREGATE FUNCTIONS & GROUP BY / HAVING
-- ============================================================================

-- Q3.1: Total students assigned per bus with remaining seat capacity
SELECT 
    b.Bus_ID,
    b.Bus_Number,
    b.Capacity AS Total_Capacity,
    COUNT(ta.Assignment_ID) AS Students_Assigned,
    (b.Capacity - COUNT(ta.Assignment_ID)) AS Available_Seats
FROM BUS b
LEFT JOIN TRANSPORT_ASSIGNMENT ta ON b.Bus_ID = ta.Bus_ID
GROUP BY b.Bus_ID, b.Bus_Number, b.Capacity
ORDER BY Students_Assigned DESC;

-- Q3.2: Routes with more than 2 assigned students (HAVING filter)
SELECT 
    r.Route_ID,
    r.Route_Name,
    r.Total_Distance,
    COUNT(ta.Assignment_ID) AS Total_Students
FROM ROUTE r
JOIN TRANSPORT_ASSIGNMENT ta ON r.Route_ID = ta.Route_ID
GROUP BY r.Route_ID, r.Route_Name, r.Total_Distance
HAVING COUNT(ta.Assignment_ID) >= 2;

-- Q3.3: Average distance and stop count across routes
SELECT 
    COUNT(DISTINCT r.Route_ID) AS Total_Routes,
    ROUND(AVG(r.Total_Distance), 2) AS Average_Route_Distance_KM,
    ROUND(AVG(sub.Stop_Count), 1) AS Average_Stops_Per_Route
FROM ROUTE r
JOIN (
    SELECT Route_ID, COUNT(Stop_ID) AS Stop_Count
    FROM BUS_STOP
    GROUP BY Route_ID
) sub ON r.Route_ID = sub.Route_ID;


-- ============================================================================
-- CATEGORY 4: NESTED SUBQUERIES (IN, EXISTS, CORRELATED)
-- ============================================================================

-- Q4.1: Subquery with IN - Find all parents whose children are on Route 401
SELECT Parent_ID, Parent_Name, Phone_Number, Relationship
FROM PARENT
WHERE Parent_ID IN (
    SELECT s.Parent_ID
    FROM STUDENT s
    JOIN TRANSPORT_ASSIGNMENT ta ON s.Student_ID = ta.Student_ID
    WHERE ta.Route_ID = 401
);

-- Q4.2: Subquery with NOT EXISTS - Identify routes that currently have no assigned students
SELECT r.Route_ID, r.Route_Name, r.Starting_Point, r.Destination
FROM ROUTE r
WHERE NOT EXISTS (
    SELECT 1 
    FROM TRANSPORT_ASSIGNMENT ta 
    WHERE ta.Route_ID = r.Route_ID
);

-- Q4.3: Correlated Subquery - List buses whose student count is below overall average
SELECT 
    b.Bus_ID, 
    b.Bus_Number, 
    b.Capacity
FROM BUS b
WHERE (
    SELECT COUNT(*) 
    FROM TRANSPORT_ASSIGNMENT ta 
    WHERE ta.Bus_ID = b.Bus_ID
) < (
    SELECT COUNT(*) / COUNT(DISTINCT Bus_ID) 
    FROM TRANSPORT_ASSIGNMENT
);


-- ============================================================================
-- CATEGORY 5: STRING PATTERN MATCHING & DATE FILTERS
-- ============================================================================

-- Q5.1: Find all stops situated near 'X Roads' or 'Circle'
SELECT Stop_ID, Stop_Name, Location, Route_ID
FROM BUS_STOP
WHERE Stop_Name LIKE '%X Roads%' OR Stop_Name LIKE '%Circle%' OR Location LIKE '%X Roads%';

-- Q5.2: Retrieve assignments created in June 2026
SELECT Assignment_ID, Student_ID, Bus_ID, Route_ID, Assignment_Date
FROM TRANSPORT_ASSIGNMENT
WHERE Assignment_Date BETWEEN '2026-06-01' AND '2026-06-30'
ORDER BY Assignment_Date ASC;

