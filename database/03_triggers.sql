-- ============================================================================
-- SCHOOL BUS ROUTE AND STUDENT TRANSPORT MANAGEMENT SYSTEM
-- SCRIPT: 03_triggers.sql
-- PURPOSE: Integrity enforcement, capacity checks, and audit logging triggers
-- DBMS TARGET: MySQL 8.0+ / MariaDB
-- ============================================================================

USE school_transport_db;

-- ----------------------------------------------------------------------------
-- AUDIT TABLE FOR ASSIGNMENT LOGGING
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ASSIGNMENT_AUDIT_LOG (
    Log_ID INT AUTO_INCREMENT PRIMARY KEY,
    Assignment_ID INT NOT NULL,
    Student_ID INT NOT NULL,
    Bus_ID INT NOT NULL,
    Route_ID INT NOT NULL,
    Stop_ID INT NOT NULL,
    Action_Type VARCHAR(20) NOT NULL,
    Log_Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    Action_User VARCHAR(50) DEFAULT 'system'
);

DELIMITER //

-- ----------------------------------------------------------------------------
-- TRIGGER 1: trg_check_bus_capacity
-- Verifies physical vehicle seating capacity before allocating a student.
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_check_bus_capacity//
CREATE TRIGGER trg_check_bus_capacity
BEFORE INSERT ON TRANSPORT_ASSIGNMENT
FOR EACH ROW
BEGIN
    DECLARE current_allocated INT DEFAULT 0;
    DECLARE bus_max_capacity INT DEFAULT 0;

    -- Retrieve bus max capacity
    SELECT Capacity INTO bus_max_capacity
    FROM BUS
    WHERE Bus_ID = NEW.Bus_ID;

    -- Count existing student allocations for this bus and academic year
    SELECT COUNT(*) INTO current_allocated
    FROM TRANSPORT_ASSIGNMENT
    WHERE Bus_ID = NEW.Bus_ID
      AND Academic_Year = NEW.Academic_Year;

    IF current_allocated >= bus_max_capacity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Operation Denied: Bus seating capacity has been fully exhausted for this academic year.';
    END IF;
END//

-- ----------------------------------------------------------------------------
-- TRIGGER 2: trg_validate_stop_route
-- Enforces that the designated pickup Stop belongs strictly to the assigned Route.
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_validate_stop_route//
CREATE TRIGGER trg_validate_stop_route
BEFORE INSERT ON TRANSPORT_ASSIGNMENT
FOR EACH ROW
BEGIN
    DECLARE stop_exists INT DEFAULT 0;

    SELECT COUNT(*) INTO stop_exists
    FROM BUS_STOP
    WHERE Stop_ID = NEW.Stop_ID
      AND Route_ID = NEW.Route_ID;

    IF stop_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Integrity Error: The selected Stop_ID does not belong to the specified Route_ID.';
    END IF;
END//

-- ----------------------------------------------------------------------------
-- TRIGGER 3: trg_audit_assignment_insert
-- Records every newly created student transport assignment into an audit log.
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_audit_assignment_insert//
CREATE TRIGGER trg_audit_assignment_insert
AFTER INSERT ON TRANSPORT_ASSIGNMENT
FOR EACH ROW
BEGIN
    INSERT INTO ASSIGNMENT_AUDIT_LOG (
        Assignment_ID, Student_ID, Bus_ID, Route_ID, Stop_ID, Action_Type, Log_Timestamp, Action_User
    ) VALUES (
        NEW.Assignment_ID, NEW.Student_ID, NEW.Bus_ID, NEW.Route_ID, NEW.Stop_ID, 'ALLOCATED', NOW(), USER()
    );
END//

DELIMITER ;

