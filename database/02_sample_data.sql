-- ============================================================================
-- SCHOOL BUS ROUTE AND STUDENT TRANSPORT MANAGEMENT SYSTEM
-- SCRIPT: 02_sample_data.sql
-- PURPOSE: Realistic DML seed records for all 7 entities
-- DBMS TARGET: MySQL 8.0+ / MariaDB
-- ============================================================================

USE school_transport_db;

-- ----------------------------------------------------------------------------
-- 1. SEED DATA: PARENT
-- ----------------------------------------------------------------------------
INSERT INTO PARENT (Parent_ID, Parent_Name, Phone_Number, Email, Relationship) VALUES
(101, 'Rajesh Sharma',    '9876543210', 'rajesh.sharma@example.com',    'Father'),
(102, 'Priya Reddy',      '9876543211', 'priya.reddy@example.com',      'Mother'),
(103, 'Venkat Rao',       '9876543212', 'venkat.rao@example.com',       'Father'),
(104, 'Sunita Varma',     '9876543213', 'sunita.varma@example.com',     'Mother'),
(105, 'Kishore Kumar',    '9876543214', 'kishore.kumar@example.com',    'Father');

-- ----------------------------------------------------------------------------
-- 2. SEED DATA: STUDENT
-- ----------------------------------------------------------------------------
INSERT INTO STUDENT (Student_ID, Student_Name, Class, Section, Gender, Address, Parent_ID) VALUES
(1001, 'Aarav Sharma',   'Grade 8',  'A', 'Male',   'Plot 12, Secunderabad',   101),
(1002, 'Ananya Sharma',  'Grade 5',  'B', 'Female', 'Plot 12, Secunderabad',   101),
(1003, 'Rohan Reddy',    'Grade 10', 'A', 'Male',   'Flat 302, Uppal Depot',   102),
(1004, 'Diya Reddy',     'Grade 7',  'C', 'Female', 'Flat 302, Uppal Depot',   102),
(1005, 'Vikram Rao',     'Grade 9',  'B', 'Male',   'H.No 4-55, ECIL X Roads', 103),
(1006, 'Sneha Varma',    'Grade 6',  'A', 'Female', 'Villa 8, Habsiguda',      104),
(1007, 'Kavya Kumar',    'Grade 11', 'A', 'Female', 'Plot 45, Malkajgiri',     105),
(1008, 'Aditya Kumar',   'Grade 8',  'B', 'Male',   'Plot 45, Malkajgiri',     105);

-- ----------------------------------------------------------------------------
-- 3. SEED DATA: DRIVER
-- ----------------------------------------------------------------------------
INSERT INTO DRIVER (Driver_ID, Driver_Name, Phone_Number, License_Number, Experience) VALUES
(201, 'Ramachander Goud', '9123456780', 'DL-TS-2015-001234', 12),
(202, 'Mohd. Khaleel',    '9123456781', 'DL-TS-2017-005678', 8),
(203, 'Bala Krishna',     '9123456782', 'DL-TS-2012-009876', 15),
(204, 'Suresh Nayak',     '9123456783', 'DL-TS-2019-003456', 5);

-- ----------------------------------------------------------------------------
-- 4. SEED DATA: BUS
-- ----------------------------------------------------------------------------
INSERT INTO BUS (Bus_ID, Driver_ID, Registration_Number, Bus_Number, Capacity, Bus_Model, Status) VALUES
(301, 201, 'TS-08-UA-1001', 'BUS-01', 30, 'Tata Starbus 34S',        'Active'),
(302, 202, 'TS-08-UA-1002', 'BUS-02', 30, 'Ashok Leyland Sunshine',  'Active'),
(303, 203, 'TS-08-UA-1003', 'BUS-03', 25, 'Eicher Starline 28S',      'Active'),
(304, 204, 'TS-08-UA-1004', 'BUS-04', 35, 'Force Traveller Cruiser',  'Active');

-- ----------------------------------------------------------------------------
-- 5. SEED DATA: ROUTE
-- ----------------------------------------------------------------------------
INSERT INTO ROUTE (Route_ID, Route_Name, Starting_Point, Destination, Total_Distance) VALUES
(401, 'North Corridor - Secunderabad Route', 'Secunderabad Station', 'School Campus (Cheeryal)', 24.50),
(402, 'East Corridor - Uppal Route',         'Uppal Metro Station',  'School Campus (Cheeryal)', 18.20),
(403, 'Central Corridor - ECIL Route',        'ECIL Crossroads',      'School Campus (Cheeryal)', 14.80);

-- ----------------------------------------------------------------------------
-- 6. SEED DATA: BUS_STOP
-- ----------------------------------------------------------------------------
INSERT INTO BUS_STOP (Stop_ID, Stop_Name, Location, Route_ID, Stop_Order) VALUES
-- Route 401: Secunderabad Route
(501, 'Secunderabad Junction', 'Near Clock Tower',           401, 1),
(502, 'Maredpally Circle',     'Opp. Heritage Fresh',        401, 2),
(503, 'Malkajgiri Geeta Nagar','Near Malkajgiri Bus Stop',   401, 3),
(504, 'Sainikpuri X Roads',    'Main Signal Point',          401, 4),

-- Route 402: Uppal Route
(505, 'Uppal Metro Station',   'Exit Gate 2 Bus Bay',        402, 1),
(506, 'Habsiguda Street 8',    'Opposite NGRI Main Gate',    402, 2),
(507, 'Nacharam Industrial',   'Near HMT Nagar Post Office', 402, 3),
(508, 'Mallapur Signal',       'Near Indian Oil Pump',       402, 4),

-- Route 403: ECIL Route
(509, 'ECIL Crossroads',       'Opp. South Indian Bank',     403, 1),
(510, 'Kushaiguda Market',     'Bus Depot Entrance',         403, 2),
(511, 'Nagaram Centre',        'Near Gram Panchayat Office', 403, 3),
(512, 'Rampally X Roads',      'Beside Reliance Smart Point',403, 4);

-- ----------------------------------------------------------------------------
-- 7. SEED DATA: TRANSPORT_ASSIGNMENT
-- ----------------------------------------------------------------------------
INSERT INTO TRANSPORT_ASSIGNMENT (Assignment_ID, Student_ID, Bus_ID, Route_ID, Stop_ID, Academic_Year, Assignment_Date) VALUES
(601, 1001, 301, 401, 501, '2026-2027', '2026-06-10'),
(602, 1002, 301, 401, 501, '2026-2027', '2026-06-10'),
(603, 1003, 302, 402, 505, '2026-2027', '2026-06-11'),
(604, 1004, 302, 402, 505, '2026-2027', '2026-06-11'),
(605, 1005, 303, 403, 509, '2026-2027', '2026-06-12'),
(606, 1006, 302, 402, 506, '2026-2027', '2026-06-12'),
(607, 1007, 301, 401, 503, '2026-2027', '2026-06-15'),
(608, 1008, 301, 401, 503, '2026-2027', '2026-06-15');

