"""
Database Initializer and Dual-Mode Setup Script
Supports:
1. SQLite (built-in, zero configuration, immediate local testing & interface execution)
2. MySQL (optional, when MySQL / XAMPP service is running)
"""

import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "school_transport.db")

SQLITE_SCHEMA = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS ASSIGNMENT_AUDIT_LOG;
DROP TABLE IF EXISTS TRANSPORT_ASSIGNMENT;
DROP TABLE IF EXISTS BUS_STOP;
DROP TABLE IF EXISTS ROUTE;
DROP TABLE IF EXISTS BUS;
DROP TABLE IF EXISTS DRIVER;
DROP TABLE IF EXISTS STUDENT;
DROP TABLE IF EXISTS PARENT;

-- 1. PARENT
CREATE TABLE PARENT (
    Parent_ID INTEGER PRIMARY KEY,
    Parent_Name TEXT NOT NULL,
    Phone_Number TEXT NOT NULL UNIQUE,
    Email TEXT,
    Relationship TEXT NOT NULL
);

-- 2. STUDENT
CREATE TABLE STUDENT (
    Student_ID INTEGER PRIMARY KEY,
    Student_Name TEXT NOT NULL,
    Class TEXT NOT NULL,
    Section TEXT NOT NULL,
    Gender TEXT NOT NULL CHECK (Gender IN ('Male', 'Female', 'Other')),
    Address TEXT NOT NULL,
    Parent_ID INTEGER NOT NULL,
    FOREIGN KEY (Parent_ID) REFERENCES PARENT(Parent_ID) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 3. DRIVER
CREATE TABLE DRIVER (
    Driver_ID INTEGER PRIMARY KEY,
    Driver_Name TEXT NOT NULL,
    Phone_Number TEXT NOT NULL UNIQUE,
    License_Number TEXT NOT NULL UNIQUE,
    Experience INTEGER NOT NULL CHECK (Experience >= 0)
);

-- 4. BUS
CREATE TABLE BUS (
    Bus_ID INTEGER PRIMARY KEY,
    Driver_ID INTEGER NOT NULL UNIQUE,
    Registration_Number TEXT NOT NULL UNIQUE,
    Bus_Number TEXT NOT NULL UNIQUE,
    Capacity INTEGER NOT NULL CHECK (Capacity > 0),
    Bus_Model TEXT NOT NULL,
    Status TEXT NOT NULL DEFAULT 'Active' CHECK (Status IN ('Active', 'Maintenance', 'Inactive')),
    FOREIGN KEY (Driver_ID) REFERENCES DRIVER(Driver_ID) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 5. ROUTE
CREATE TABLE ROUTE (
    Route_ID INTEGER PRIMARY KEY,
    Route_Name TEXT NOT NULL UNIQUE,
    Starting_Point TEXT NOT NULL,
    Destination TEXT NOT NULL,
    Total_Distance REAL NOT NULL CHECK (Total_Distance > 0.0)
);

-- 6. BUS_STOP
CREATE TABLE BUS_STOP (
    Stop_ID INTEGER PRIMARY KEY,
    Stop_Name TEXT NOT NULL,
    Location TEXT NOT NULL,
    Route_ID INTEGER NOT NULL,
    Stop_Order INTEGER NOT NULL CHECK (Stop_Order > 0),
    FOREIGN KEY (Route_ID) REFERENCES ROUTE(Route_ID) ON UPDATE CASCADE ON DELETE CASCADE,
    UNIQUE (Route_ID, Stop_Order),
    UNIQUE (Route_ID, Stop_ID)
);

-- 7. TRANSPORT_ASSIGNMENT
CREATE TABLE TRANSPORT_ASSIGNMENT (
    Assignment_ID INTEGER PRIMARY KEY,
    Student_ID INTEGER NOT NULL,
    Bus_ID INTEGER NOT NULL,
    Route_ID INTEGER NOT NULL,
    Stop_ID INTEGER NOT NULL,
    Academic_Year TEXT NOT NULL,
    Assignment_Date TEXT NOT NULL,
    FOREIGN KEY (Student_ID) REFERENCES STUDENT(Student_ID) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (Bus_ID) REFERENCES BUS(Bus_ID) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (Route_ID) REFERENCES ROUTE(Route_ID) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (Stop_ID) REFERENCES BUS_STOP(Stop_ID) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (Route_ID, Stop_ID) REFERENCES BUS_STOP(Route_ID, Stop_ID) ON UPDATE CASCADE ON DELETE RESTRICT,
    UNIQUE (Student_ID, Academic_Year)
);

-- AUDIT TABLE
CREATE TABLE ASSIGNMENT_AUDIT_LOG (
    Log_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Assignment_ID INTEGER NOT NULL,
    Student_ID INTEGER NOT NULL,
    Bus_ID INTEGER NOT NULL,
    Route_ID INTEGER NOT NULL,
    Stop_ID INTEGER NOT NULL,
    Action_Type TEXT NOT NULL,
    Log_Timestamp TEXT DEFAULT (datetime('now','localtime')),
    Action_User TEXT DEFAULT 'admin'
);

-- TRIGGERS
CREATE TRIGGER trg_check_bus_capacity
BEFORE INSERT ON TRANSPORT_ASSIGNMENT
FOR EACH ROW
WHEN (
    SELECT COUNT(*) FROM TRANSPORT_ASSIGNMENT 
    WHERE Bus_ID = NEW.Bus_ID AND Academic_Year = NEW.Academic_Year
) >= (
    SELECT Capacity FROM BUS WHERE Bus_ID = NEW.Bus_ID
)
BEGIN
    SELECT RAISE(ABORT, 'Operation Denied: Bus seating capacity has been fully exhausted for this academic year.');
END;

CREATE TRIGGER trg_validate_stop_route
BEFORE INSERT ON TRANSPORT_ASSIGNMENT
FOR EACH ROW
WHEN (
    SELECT COUNT(*) FROM BUS_STOP 
    WHERE Stop_ID = NEW.Stop_ID AND Route_ID = NEW.Route_ID
) = 0
BEGIN
    SELECT RAISE(ABORT, 'Integrity Error: The selected Stop_ID does not belong to the specified Route_ID.');
END;

CREATE TRIGGER trg_audit_assignment_insert
AFTER INSERT ON TRANSPORT_ASSIGNMENT
FOR EACH ROW
BEGIN
    INSERT INTO ASSIGNMENT_AUDIT_LOG (
        Assignment_ID, Student_ID, Bus_ID, Route_ID, Stop_ID, Action_Type
    ) VALUES (
        NEW.Assignment_ID, NEW.Student_ID, NEW.Bus_ID, NEW.Route_ID, NEW.Stop_ID, 'ALLOCATED'
    );
END;

-- VIEWS
CREATE VIEW vw_student_transport_details AS
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

CREATE VIEW vw_route_operational_summary AS
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

CREATE VIEW vw_bus_fleet_status AS
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

CREATE VIEW vw_bus_occupancy_summary AS
SELECT 
    b.Bus_ID,
    b.Bus_Number,
    b.Capacity AS Total_Capacity,
    COUNT(ta.Assignment_ID) AS Students_Assigned,
    (b.Capacity - COUNT(ta.Assignment_ID)) AS Available_Seats,
    ROUND((CAST(COUNT(ta.Assignment_ID) AS REAL) / b.Capacity) * 100.0, 2) AS Utilization_Percentage
FROM BUS b
LEFT JOIN TRANSPORT_ASSIGNMENT ta ON b.Bus_ID = ta.Bus_ID
GROUP BY b.Bus_ID, b.Bus_Number, b.Capacity;
"""

SQLITE_SEED_DATA = """
-- 1. PARENT
INSERT INTO PARENT (Parent_ID, Parent_Name, Phone_Number, Email, Relationship) VALUES
(101, 'Rajesh Sharma',    '9876543210', 'rajesh.sharma@example.com',    'Father'),
(102, 'Priya Reddy',      '9876543211', 'priya.reddy@example.com',      'Mother'),
(103, 'Venkat Rao',       '9876543212', 'venkat.rao@example.com',       'Father'),
(104, 'Sunita Varma',     '9876543213', 'sunita.varma@example.com',     'Mother'),
(105, 'Kishore Kumar',    '9876543214', 'kishore.kumar@example.com',    'Father');

-- 2. STUDENT
INSERT INTO STUDENT (Student_ID, Student_Name, Class, Section, Gender, Address, Parent_ID) VALUES
(1001, 'Aarav Sharma',   'Grade 8',  'A', 'Male',   'Plot 12, Secunderabad',   101),
(1002, 'Ananya Sharma',  'Grade 5',  'B', 'Female', 'Plot 12, Secunderabad',   101),
(1003, 'Rohan Reddy',    'Grade 10', 'A', 'Male',   'Flat 302, Uppal Depot',   102),
(1004, 'Diya Reddy',     'Grade 7',  'C', 'Female', 'Flat 302, Uppal Depot',   102),
(1005, 'Vikram Rao',     'Grade 9',  'B', 'Male',   'H.No 4-55, ECIL X Roads', 103),
(1006, 'Sneha Varma',    'Grade 6',  'A', 'Female', 'Villa 8, Habsiguda',      104),
(1007, 'Kavya Kumar',    'Grade 11', 'A', 'Female', 'Plot 45, Malkajgiri',     105),
(1008, 'Aditya Kumar',   'Grade 8',  'B', 'Male',   'Plot 45, Malkajgiri',     105);

-- 3. DRIVER
INSERT INTO DRIVER (Driver_ID, Driver_Name, Phone_Number, License_Number, Experience) VALUES
(201, 'Ramachander Goud', '9123456780', 'DL-TS-2015-001234', 12),
(202, 'Mohd. Khaleel',    '9123456781', 'DL-TS-2017-005678', 8),
(203, 'Bala Krishna',     '9123456782', 'DL-TS-2012-009876', 15),
(204, 'Suresh Nayak',     '9123456783', 'DL-TS-2019-003456', 5);

-- 4. BUS
INSERT INTO BUS (Bus_ID, Driver_ID, Registration_Number, Bus_Number, Capacity, Bus_Model, Status) VALUES
(301, 201, 'TS-08-UA-1001', 'BUS-01', 30, 'Tata Starbus 34S',        'Active'),
(302, 202, 'TS-08-UA-1002', 'BUS-02', 30, 'Ashok Leyland Sunshine',  'Active'),
(303, 203, 'TS-08-UA-1003', 'BUS-03', 25, 'Eicher Starline 28S',      'Active'),
(304, 204, 'TS-08-UA-1004', 'BUS-04', 35, 'Force Traveller Cruiser',  'Active');

-- 5. ROUTE
INSERT INTO ROUTE (Route_ID, Route_Name, Starting_Point, Destination, Total_Distance) VALUES
(401, 'North Corridor - Secunderabad Route', 'Secunderabad Station', 'School Campus (Cheeryal)', 24.50),
(402, 'East Corridor - Uppal Route',         'Uppal Metro Station',  'School Campus (Cheeryal)', 18.20),
(403, 'Central Corridor - ECIL Route',        'ECIL Crossroads',      'School Campus (Cheeryal)', 14.80);

-- 6. BUS_STOP
INSERT INTO BUS_STOP (Stop_ID, Stop_Name, Location, Route_ID, Stop_Order) VALUES
(501, 'Secunderabad Junction', 'Near Clock Tower',           401, 1),
(502, 'Maredpally Circle',     'Opp. Heritage Fresh',        401, 2),
(503, 'Malkajgiri Geeta Nagar','Near Malkajgiri Bus Stop',   401, 3),
(504, 'Sainikpuri X Roads',    'Main Signal Point',          401, 4),
(505, 'Uppal Metro Station',   'Exit Gate 2 Bus Bay',        402, 1),
(506, 'Habsiguda Street 8',    'Opposite NGRI Main Gate',    402, 2),
(507, 'Nacharam Industrial',   'Near HMT Nagar Post Office', 402, 3),
(508, 'Mallapur Signal',       'Near Indian Oil Pump',       402, 4),
(509, 'ECIL Crossroads',       'Opp. South Indian Bank',     403, 1),
(510, 'Kushaiguda Market',     'Bus Depot Entrance',         403, 2),
(511, 'Nagaram Centre',        'Near Gram Panchayat Office', 403, 3),
(512, 'Rampally X Roads',      'Beside Reliance Smart Point',403, 4);

-- 7. TRANSPORT_ASSIGNMENT
INSERT INTO TRANSPORT_ASSIGNMENT (Assignment_ID, Student_ID, Bus_ID, Route_ID, Stop_ID, Academic_Year, Assignment_Date) VALUES
(601, 1001, 301, 401, 501, '2026-2027', '2026-06-10'),
(602, 1002, 301, 401, 501, '2026-2027', '2026-06-10'),
(603, 1003, 302, 402, 505, '2026-2027', '2026-06-11'),
(604, 1004, 302, 402, 505, '2026-2027', '2026-06-11'),
(605, 1005, 303, 403, 509, '2026-2027', '2026-06-12'),
(606, 1006, 302, 402, 506, '2026-2027', '2026-06-12'),
(607, 1007, 301, 401, 503, '2026-2027', '2026-06-15'),
(608, 1008, 301, 401, 503, '2026-2027', '2026-06-15');
"""

def init_sqlite_db():
    print(f"Initializing SQLite database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(SQLITE_SCHEMA)
    cursor.executescript(SQLITE_SEED_DATA)
    conn.commit()

    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
    print(f"Verified {len(tables)} tables created: {tables}")

    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t};")
        count = cursor.fetchone()[0]
        print(f"  - Table {t}: {count} records")

    conn.close()
    print("SQLite database successfully initialized and verified!")

if __name__ == "__main__":
    init_sqlite_db()

