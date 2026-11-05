-- ============================================================================
-- SCHOOL BUS ROUTE AND STUDENT TRANSPORT MANAGEMENT SYSTEM
-- SCRIPT: 04_procedures.sql
-- PURPOSE: Business logic stored procedures with transaction handling
-- DBMS TARGET: MySQL 8.0+ / MariaDB
-- ============================================================================

USE school_transport_db;

DELIMITER //

-- ----------------------------------------------------------------------------
-- PROCEDURE 1: sp_allocate_student_transport
-- Safely assigns a student to a bus, route, and stop within an ACID transaction.
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_allocate_student_transport//
CREATE PROCEDURE sp_allocate_student_transport(
    IN p_student_id INT,
    IN p_bus_id INT,
    IN p_route_id INT,
    IN p_stop_id INT,
    IN p_academic_year VARCHAR(15),
    OUT p_result_code VARCHAR(20),
    OUT p_result_message VARCHAR(255)
)
proc_label: BEGIN
    DECLARE v_new_assignment_id INT DEFAULT 601;
    DECLARE v_existing_count INT DEFAULT 0;
    DECLARE v_bus_cap INT DEFAULT 0;
    DECLARE v_current_assigned INT DEFAULT 0;
    DECLARE v_valid_stop INT DEFAULT 0;

    -- Error handler for unexpected SQL exceptions
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result_code = 'ERROR';
        SET p_result_message = 'Transaction rolled back due to an unexpected SQL exception.';
    END;

    -- 1. Check if student already allocated for the academic year
    SELECT COUNT(*) INTO v_existing_count
    FROM TRANSPORT_ASSIGNMENT
    WHERE Student_ID = p_student_id
      AND Academic_Year = p_academic_year;

    IF v_existing_count > 0 THEN
        SET p_result_code = 'DUPLICATE';
        SET p_result_message = 'Student already has an active assignment for this academic year.';
        LEAVE proc_label;
    END IF;

    -- 2. Verify Stop belongs to the designated Route
    SELECT COUNT(*) INTO v_valid_stop
    FROM BUS_STOP
    WHERE Stop_ID = p_stop_id
      AND Route_ID = p_route_id;

    IF v_valid_stop = 0 THEN
        SET p_result_code = 'INVALID_STOP';
        SET p_result_message = 'The specified bus stop does not belong to the selected route.';
        LEAVE proc_label;
    END IF;

    -- 3. Check Bus Seating Availability
    SELECT Capacity INTO v_bus_cap FROM BUS WHERE Bus_ID = p_bus_id;
    SELECT COUNT(*) INTO v_current_assigned FROM TRANSPORT_ASSIGNMENT
    WHERE Bus_ID = p_bus_id AND Academic_Year = p_academic_year;

    IF v_current_assigned >= v_bus_cap THEN
        SET p_result_code = 'BUS_FULL';
        SET p_result_message = 'Cannot allocate: Selected bus has no remaining seats.';
        LEAVE proc_label;
    END IF;

    -- Compute next surrogate ID
    SELECT IFNULL(MAX(Assignment_ID), 600) + 1 INTO v_new_assignment_id FROM TRANSPORT_ASSIGNMENT;

    -- 4. Execute atomic transaction
    START TRANSACTION;
        INSERT INTO TRANSPORT_ASSIGNMENT (
            Assignment_ID, Student_ID, Bus_ID, Route_ID, Stop_ID, Academic_Year, Assignment_Date
        ) VALUES (
            v_new_assignment_id, p_student_id, p_bus_id, p_route_id, p_stop_id, p_academic_year, CURDATE()
        );
    COMMIT;

    SET p_result_code = 'SUCCESS';
    SET p_result_message = CONCAT('Student successfully assigned. Assignment ID: ', v_new_assignment_id);
END//

-- ----------------------------------------------------------------------------
-- PROCEDURE 2: sp_get_route_student_manifest
-- Retrieves sequential stop-by-stop passenger list for a given route.
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_get_route_student_manifest//
CREATE PROCEDURE sp_get_route_student_manifest(
    IN p_route_id INT
)
BEGIN
    SELECT 
        bs.Stop_Order,
        bs.Stop_Name,
        bs.Location AS Stop_Location,
        s.Student_ID,
        s.Student_Name,
        s.Class,
        s.Section,
        p.Parent_Name,
        p.Phone_Number AS Emergency_Contact,
        b.Bus_Number,
        d.Driver_Name,
        d.Phone_Number AS Driver_Phone
    FROM TRANSPORT_ASSIGNMENT ta
    JOIN BUS_STOP bs ON ta.Stop_ID = bs.Stop_ID
    JOIN STUDENT s ON ta.Student_ID = s.Student_ID
    JOIN PARENT p ON s.Parent_ID = p.Parent_ID
    JOIN BUS b ON ta.Bus_ID = b.Bus_ID
    JOIN DRIVER d ON b.Driver_ID = d.Driver_ID
    WHERE ta.Route_ID = p_route_id
    ORDER BY bs.Stop_Order ASC, s.Student_Name ASC;
END//

-- ----------------------------------------------------------------------------
-- PROCEDURE 3: sp_get_bus_utilization_report
-- Generates real-time occupancy statistics across all school buses.
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_get_bus_utilization_report//
CREATE PROCEDURE sp_get_bus_utilization_report()
BEGIN
    SELECT 
        b.Bus_ID,
        b.Bus_Number,
        b.Registration_Number,
        b.Bus_Model,
        d.Driver_Name,
        d.Phone_Number AS Driver_Contact,
        b.Capacity AS Total_Seats,
        COUNT(ta.Assignment_ID) AS Occupied_Seats,
        (b.Capacity - COUNT(ta.Assignment_ID)) AS Available_Seats,
        ROUND((COUNT(ta.Assignment_ID) / b.Capacity) * 100.0, 2) AS Utilization_Percentage,
        b.Status
    FROM BUS b
    JOIN DRIVER d ON b.Driver_ID = d.Driver_ID
    LEFT JOIN TRANSPORT_ASSIGNMENT ta ON b.Bus_ID = ta.Bus_ID
    GROUP BY b.Bus_ID, b.Bus_Number, b.Registration_Number, b.Bus_Model, d.Driver_Name, d.Phone_Number, b.Capacity, b.Status
    ORDER BY b.Bus_ID ASC;
END//

DELIMITER ;

