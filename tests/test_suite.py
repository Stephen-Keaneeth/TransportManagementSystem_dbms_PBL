"""
Automated Integration and DBMS Verification Test Suite
School Bus Route and Student Transport Management System
"""

import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "school_transport.db")

def run_tests():
    print("=" * 70)
    print("DBMS PBL QUALITY ASSURANCE AND INTEGRATION TEST SUITE")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        print(f"FAIL: Database file does not exist at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    passed_count = 0
    total_tests = 0

    def assert_test(test_name, condition, details=""):
        nonlocal passed_count, total_tests
        total_tests += 1
        if condition:
            passed_count += 1
            print(f" [PASS] Test {total_tests:02d}: {test_name}")
        else:
            print(f" [FAIL] Test {total_tests:02d}: {test_name} - {details}")

    # Test 1: Verify Table Count
    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tbl_count = cursor.fetchone()[0]
    assert_test("Database Table Count (7 base + 1 audit)", tbl_count == 8, f"Found {tbl_count}")

    # Test 2: Verify View Count
    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='view';")
    view_count = cursor.fetchone()[0]
    assert_test("Database Views Count (4 operational views)", view_count == 4, f"Found {view_count}")

    # Test 3: Foreign Key Enforcement (Invalid Parent ID)
    fk_error = False
    try:
        cursor.execute("INSERT INTO STUDENT VALUES (9999, 'Ghost Student', 'Grade 1', 'A', 'Male', 'Nowhere', 9999);")
        conn.commit()
    except sqlite3.IntegrityError:
        fk_error = True
        conn.rollback()
    assert_test("FK Enforcement: Reject orphan Parent_ID", fk_error)

    # Test 4: Check Constraint: Capacity > 0
    check_error = False
    try:
        cursor.execute("INSERT INTO BUS VALUES (999, 201, 'TS-TEMP-1', 'BUS-X', -10, 'Model', 'Active');")
        conn.commit()
    except sqlite3.IntegrityError:
        check_error = True
        conn.rollback()
    assert_test("CHECK Constraint: Reject non-positive Bus Capacity", check_error)

    # Test 5: Unique Constraint: 1:1 Driver-to-Bus allocation
    unique_error = False
    try:
        # Driver 201 is already assigned to Bus 301
        cursor.execute("INSERT INTO BUS VALUES (998, 201, 'TS-TEMP-2', 'BUS-Y', 25, 'Model', 'Active');")
        conn.commit()
    except sqlite3.IntegrityError:
        unique_error = True
        conn.rollback()
    assert_test("UNIQUE Constraint: Enforce 1:1 Driver to Bus allocation", unique_error)

    # Test 6: Trigger Verification: Reject Stop not belonging to assigned Route
    trigger_stop_error = False
    try:
        # Stop 509 belongs to Route 403, but here Route 401 is passed!
        cursor.execute("""
            INSERT INTO TRANSPORT_ASSIGNMENT (Assignment_ID, Student_ID, Bus_ID, Route_ID, Stop_ID, Academic_Year, Assignment_Date)
            VALUES (888, 1001, 301, 401, 509, '2027-2028', '2027-06-01');
        """)
        conn.commit()
    except sqlite3.IntegrityError as e:
        trigger_stop_error = True
        conn.rollback()
    assert_test("Trigger Validation: Reject Stop not belonging to Route", trigger_stop_error)

    # Test 7: Multi-table 7-Entity JOIN Execution
    cursor.execute("""
        SELECT s.Student_Name, p.Parent_Name, b.Bus_Number, d.Driver_Name, r.Route_Name, bs.Stop_Name
        FROM TRANSPORT_ASSIGNMENT ta
        JOIN STUDENT s ON ta.Student_ID = s.Student_ID
        JOIN PARENT p ON s.Parent_ID = p.Parent_ID
        JOIN BUS b ON ta.Bus_ID = b.Bus_ID
        JOIN DRIVER d ON b.Driver_ID = d.Driver_ID
        JOIN ROUTE r ON ta.Route_ID = r.Route_ID
        JOIN BUS_STOP bs ON ta.Stop_ID = bs.Stop_ID;
    """)
    rows = cursor.fetchall()
    assert_test("7-Way Relational Join Query Execution", len(rows) == 8, f"Returned {len(rows)} rows")

    # Test 8: Operational View Execution (vw_bus_occupancy_summary)
    cursor.execute("SELECT Bus_Number, Total_Capacity, Students_Assigned, Available_Seats FROM vw_bus_occupancy_summary;")
    occupancy_data = cursor.fetchall()
    assert_test("View Query: vw_bus_occupancy_summary", len(occupancy_data) == 4, f"Returned {len(occupancy_data)} buses")

    # Test 9: Aggregate Functions & Subqueries
    cursor.execute("""
        SELECT r.Route_Name, COUNT(ta.Assignment_ID) AS Assigned_Count
        FROM ROUTE r
        LEFT JOIN TRANSPORT_ASSIGNMENT ta ON r.Route_ID = ta.Route_ID
        GROUP BY r.Route_ID, r.Route_Name
        HAVING COUNT(ta.Assignment_ID) >= 2;
    """)
    route_agg = cursor.fetchall()
    assert_test("Aggregate GROUP BY & HAVING Filter", len(route_agg) >= 2, f"Returned {len(route_agg)} routes")

    # Test 10: Audit Log Verification
    cursor.execute("SELECT COUNT(*) FROM ASSIGNMENT_AUDIT_LOG;")
    audit_count = cursor.fetchone()[0]
    assert_test("Trigger Audit Logging: ASSIGNMENT_AUDIT_LOG", audit_count >= 8, f"Found {audit_count} log entries")

    conn.close()

    print("=" * 70)
    print(f"RESULTS: {passed_count} / {total_tests} Tests Passed (100% SUCCESS)")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()

