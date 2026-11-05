-- ============================================================================
-- SCHOOL BUS ROUTE AND STUDENT TRANSPORT MANAGEMENT SYSTEM
-- SCRIPT: 01_schema.sql
-- PURPOSE: DDL for database and all 7 relational tables with constraints
-- DBMS TARGET: MySQL 8.0+
-- ============================================================================

-- Create and select database
CREATE DATABASE IF NOT EXISTS school_transport_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE school_transport_db;

-- Disable foreign key checks during schema rebuild
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS TRANSPORT_ASSIGNMENT;
DROP TABLE IF EXISTS BUS_STOP;
DROP TABLE IF EXISTS ROUTE;
DROP TABLE IF EXISTS BUS;
DROP TABLE IF EXISTS DRIVER;
DROP TABLE IF EXISTS STUDENT;
DROP TABLE IF EXISTS PARENT;

SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- 1. PARENT TABLE
-- Stores parent / guardian contact details.
-- ----------------------------------------------------------------------------
CREATE TABLE PARENT (
    Parent_ID INT NOT NULL,
    Parent_Name VARCHAR(100) NOT NULL,
    Phone_Number VARCHAR(15) NOT NULL UNIQUE,
    Email VARCHAR(100),
    Relationship VARCHAR(50) NOT NULL,
    CONSTRAINT pk_parent PRIMARY KEY (Parent_ID)
) ;

-- ----------------------------------------------------------------------------
-- 2. STUDENT TABLE
-- Stores student profiles, class, section, address, and links to Parent.
-- ----------------------------------------------------------------------------
CREATE TABLE STUDENT (
    Student_ID INT NOT NULL,
    Student_Name VARCHAR(100) NOT NULL,
    Class VARCHAR(20) NOT NULL,
    Section VARCHAR(10) NOT NULL,
    Gender VARCHAR(10) NOT NULL,
    Address VARCHAR(255) NOT NULL,
    Parent_ID INT NOT NULL,
    CONSTRAINT pk_student PRIMARY KEY (Student_ID),
    CONSTRAINT fk_student_parent FOREIGN KEY (Parent_ID)
        REFERENCES PARENT(Parent_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_student_gender CHECK (Gender IN ('Male', 'Female', 'Other'))
)  ;

-- ----------------------------------------------------------------------------
-- 3. DRIVER TABLE
-- Stores bus driver personal, contact, and licensing details.
-- ----------------------------------------------------------------------------
CREATE TABLE DRIVER (
    Driver_ID INT NOT NULL,
    Driver_Name VARCHAR(100) NOT NULL,
    Phone_Number VARCHAR(15) NOT NULL UNIQUE,
    License_Number VARCHAR(50) NOT NULL UNIQUE,
    Experience INT NOT NULL,
    CONSTRAINT pk_driver PRIMARY KEY (Driver_ID),
    CONSTRAINT chk_driver_experience CHECK (Experience >= 0)
)  ;

-- ----------------------------------------------------------------------------
-- 4. BUS TABLE
-- Stores vehicle information and enforces 1:1 allocation with Driver.
-- ----------------------------------------------------------------------------
CREATE TABLE BUS (
    Bus_ID INT NOT NULL,
    Driver_ID INT NOT NULL UNIQUE,
    Registration_Number VARCHAR(30) NOT NULL UNIQUE,
    Bus_Number VARCHAR(20) NOT NULL UNIQUE,
    Capacity INT NOT NULL,
    Bus_Model VARCHAR(50) NOT NULL,
    Status VARCHAR(20) NOT NULL DEFAULT 'Active',
    CONSTRAINT pk_bus PRIMARY KEY (Bus_ID),
    CONSTRAINT fk_bus_driver FOREIGN KEY (Driver_ID)
        REFERENCES DRIVER(Driver_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_bus_capacity CHECK (Capacity > 0),
    CONSTRAINT chk_bus_status CHECK (Status IN ('Active', 'Maintenance', 'Inactive'))
)  ;

-- ----------------------------------------------------------------------------
-- 5. ROUTE TABLE
-- Stores route definitions, start/end locations, and total distances.
-- ----------------------------------------------------------------------------
CREATE TABLE ROUTE (
    Route_ID INT NOT NULL,
    Route_Name VARCHAR(100) NOT NULL UNIQUE,
    Starting_Point VARCHAR(100) NOT NULL,
    Destination VARCHAR(100) NOT NULL,
    Total_Distance DECIMAL(6,2) NOT NULL,
    CONSTRAINT pk_route PRIMARY KEY (Route_ID),
    CONSTRAINT chk_route_distance CHECK (Total_Distance > 0.0)
)  ;

-- ----------------------------------------------------------------------------
-- 6. BUS_STOP TABLE
-- Stores designated stops along a specific route and their sequence.
-- ----------------------------------------------------------------------------
CREATE TABLE BUS_STOP (
    Stop_ID INT NOT NULL,
    Stop_Name VARCHAR(100) NOT NULL,
    Location VARCHAR(150) NOT NULL,
    Route_ID INT NOT NULL,
    Stop_Order INT NOT NULL,
    CONSTRAINT pk_bus_stop PRIMARY KEY (Stop_ID),
    CONSTRAINT fk_stop_route FOREIGN KEY (Route_ID)
        REFERENCES ROUTE(Route_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT chk_stop_order CHECK (Stop_Order > 0),
    CONSTRAINT uq_route_stop_order UNIQUE (Route_ID, Stop_Order),
    CONSTRAINT uq_route_stop UNIQUE (Route_ID, Stop_ID)
)  ;

-- ----------------------------------------------------------------------------
-- 7. TRANSPORT_ASSIGNMENT TABLE
-- Allocates a student to a bus, route, and pickup stop for an academic year.
-- Composite FK ensures Stop_ID belongs to the assigned Route_ID.
-- ----------------------------------------------------------------------------
CREATE TABLE TRANSPORT_ASSIGNMENT (
    Assignment_ID INT NOT NULL,
    Student_ID INT NOT NULL,
    Bus_ID INT NOT NULL,
    Route_ID INT NOT NULL,
    Stop_ID INT NOT NULL,
    Academic_Year VARCHAR(15) NOT NULL,
    Assignment_Date DATE NOT NULL,
    CONSTRAINT pk_transport_assignment PRIMARY KEY (Assignment_ID),
    CONSTRAINT fk_assign_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_assign_bus FOREIGN KEY (Bus_ID)
        REFERENCES BUS(Bus_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_assign_route FOREIGN KEY (Route_ID)
        REFERENCES ROUTE(Route_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_assign_stop FOREIGN KEY (Stop_ID)
        REFERENCES BUS_STOP(Stop_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_assign_route_stop_match FOREIGN KEY (Route_ID, Stop_ID)
        REFERENCES BUS_STOP(Route_ID, Stop_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT uq_student_academic_year UNIQUE (Student_ID, Academic_Year)
)  ;

