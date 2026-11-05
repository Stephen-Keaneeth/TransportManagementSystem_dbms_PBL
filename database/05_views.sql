-- ============================================================================
-- SCHOOL BUS ROUTE AND STUDENT TRANSPORT MANAGEMENT SYSTEM
-- SCRIPT: 05_views.sql
-- PURPOSE: Relational views for operations, reporting, and abstraction
-- DBMS TARGET: MySQL 8.0+ / MariaDB
-- ============================================================================

USE school_transport_db;

-- ----------------------------------------------------------------------------
-- VIEW 1: vw_student_transport_details
-- Denormalized administrative view connecting all seven entities.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_student_transport_details AS
SELECT 
    ta.Assignment_ID,
    ta.Academic_Year,
    ta.Assignment_Date,
    s.Student_ID,
    s.Student_Name,
    s.Class,
    s.Section,
    s.Gender,
    s.Address AS Student_Address,
    p.Parent_ID,
    p.Parent_Name,
    p.Phone_Number AS Parent_Phone,
    p.Relationship AS Parent_Relation,
    b.Bus_ID,
    b.Bus_Number,
    b.Registration_Number,
    d.Driver_Name,
    d.Phone_Number AS Driver_Phone,
    r.Route_ID,
    r.Route_Name,
    r.Starting_Point,
    r.Destination,
    bs.Stop_ID,
    bs.Stop_Name,
    bs.Location AS Stop_Location,
    bs.Stop_Order
FROM TRANSPORT_ASSIGNMENT ta
JOIN STUDENT s ON ta.Student_ID = s.Student_ID
JOIN PARENT p ON s.Parent_ID = p.Parent_ID
JOIN BUS b ON ta.Bus_ID = b.Bus_ID
JOIN DRIVER d ON b.Driver_ID = d.Driver_ID
JOIN ROUTE r ON ta.Route_ID = r.Route_ID
JOIN BUS_STOP bs ON ta.Stop_ID = bs.Stop_ID;

-- ----------------------------------------------------------------------------
-- VIEW 2: vw_route_operational_summary
-- Aggregated summary of routes, total designated stops, and assigned students.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_route_operational_summary AS
SELECT 
    r.Route_ID,
    r.Route_Name,
    r.Starting_Point,
    r.Destination,
    r.Total_Distance,
    COUNT(DISTINCT bs.Stop_ID) AS Total_Stops,
    COUNT(DISTINCT ta.Assignment_ID) AS Total_Students_Assigned
FROM ROUTE r
LEFT JOIN BUS_STOP bs ON r.Route_ID = bs.Route_ID
LEFT JOIN TRANSPORT_ASSIGNMENT ta ON r.Route_ID = ta.Route_ID
GROUP BY r.Route_ID, r.Route_Name, r.Starting_Point, r.Destination, r.Total_Distance;

-- ----------------------------------------------------------------------------
-- VIEW 3: vw_bus_fleet_status
-- Overview of all buses, assigned drivers, and active status.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_bus_fleet_status AS
SELECT 
    b.Bus_ID,
    b.Bus_Number,
    b.Registration_Number,
    b.Bus_Model,
    b.Capacity,
    b.Status,
    d.Driver_ID,
    d.Driver_Name,
    d.Phone_Number AS Driver_Phone,
    d.License_Number,
    d.Experience AS Driver_Experience_Years
FROM BUS b
JOIN DRIVER d ON b.Driver_ID = d.Driver_ID;

