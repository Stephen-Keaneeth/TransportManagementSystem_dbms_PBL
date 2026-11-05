"""
Database Connection & Query Execution Handler
Supports dual modes:
# 1. SQLite (default, zero-configuration local file)#
2. MySQL (when MySQL credentials and service are active)
"""

import os
# import sqlite3
import pymysql
import time


# MySQL Config

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "school_transport_db",
    "cursorclass": pymysql.cursors.DictCursor
}



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "school_transport.db")

class DatabaseManager:
    def __init__(self, db_path=DB_PATH, config=None):
        self.db_path = db_path
        self.config = config or DB_CONFIG

    # def get_connection(self):
    #     conn = sqlite3.connect(self.db_path)
    #     conn.execute("PRAGMA foreign_keys = ON;")
    #     conn.row_factory = sqlite3.Row
    #     return conn
    def get_connection(self):
        return pymysql.connect(**self.config)

    def test_connection(self):
        try:
            conn = self.get_connection()
            conn.close()
            return {"success": True, "message": "MySQL connection successful"}
        except Exception as e:
            return {"success": False, "message": f"MySQL connection failed: {str(e)}"}


    def execute_query(self, sql_query):

        start_time = time.time()
        conn=None
        sql_clean = sql_query.strip()
        is_select = sql_clean.upper().startswith(("SELECT", "SHOW", "DESCRIBE", "EXPLAIN"))
        
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql_query)
                elapsed = round((time.time() - start_time)*1000, 2)

                if is_select:
                    rows = cursor.fetchall()
                    columns = list(rows[0].keys()) if rows else []
                    data = [list(r.values()) for r in rows]
                    return{
                        "success": True,
                        "is_select":True,
                        "columns":columns,
                        "rows":data,
                        "row_count":len(data),
                        "execution_time_ms":elapsed,
                        "message":f"Query returned {len(data)} row(s) in {elapsed} ms"
                    }
                else:
                    conn.commit()
                    affected = cursor.rowcount
                    return{
                        "success": True,
                        "is_select":False,
                        "affected_rows":affected,
                        "execution_time_ms":elapsed,
                        "message":f"Query executed successfully. Affected rows: {affected} ({elapsed} ms)."
                    }

        except Exception as e:
            if conn:
                conn.rollback()
            elapsed = round((time.time() - start_time)*1000, 2)
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": elapsed,
                "message": f"SQL Error: {str(e)}"
            }
        finally:
            if conn:
                conn.close()

                        


    # def execute_query(self, sql_query, params=None):
    #     """
    #     Executes arbitrary SQL query (SELECT, INSERT, UPDATE, DELETE).
    #     Returns a dictionary with execution status, columns, rows, execution time, and message.
    #     """
    #     start_time = time.time()
    #     conn = self.get_connection()
    #     cursor = conn.cursor()
    #     sql_clean = sql_query.strip()
    #     is_select = sql_clean.upper().startswith(("SELECT", "PRAGMA", "EXPLAIN"))

    #     try:
    #         if params:
    #             cursor.execute(sql_query, params)
    #         else:
    #             cursor.execute(sql_query)

    #         if is_select:
    #             rows = cursor.fetchall()
    #             columns = [col[0] for col in cursor.description] if cursor.description else []
    #             data = [list(row) for row in rows]
    #             elapsed = round((time.time() - start_time) * 1000, 2)
    #             return {
    #                 "success": True,
    #                 "is_select": True,
    #                 "columns": columns,
    #                 "rows": data,
    #                 "row_count": len(data),
    #                 "execution_time_ms": elapsed,
    #                 "message": f"Query returned {len(data)} row(s) in {elapsed} ms."
    #             }
    #         else:
    #             conn.commit()
    #             affected = cursor.rowcount
    #             elapsed = round((time.time() - start_time) * 1000, 2)
    #             return {
    #                 "success": True,
    #                 "is_select": False,
    #                 "affected_rows": affected,
    #                 "execution_time_ms": elapsed,
    #                 "message": f"Query executed successfully. Affected rows: {affected} ({elapsed} ms)."
    #             }
    #     except sqlite3.Error as e:
    #         conn.rollback()
    #         elapsed = round((time.time() - start_time) * 1000, 2)
    #         return {
    #             "success": False,
    #             "error": str(e),
    #             "execution_time_ms": elapsed,
    #             "message": f"SQL Error: {str(e)}"
    #         }
    #     finally:
    #         conn.close()

    # def allocate_student(self, student_id, bus_id, route_id, stop_id, academic_year):
    #     """
    #     Emulates the stored procedure sp_allocate_student_transport with ACID transaction.
    #     """
    #     conn = self.get_connection()
    #     cursor = conn.cursor()
    #     try:
    #         # 1. Check duplicate assignment
    #         cursor.execute("""
    #             SELECT COUNT(*) FROM TRANSPORT_ASSIGNMENT 
    #             WHERE Student_ID = ? AND Academic_Year = ?
    #         """, (student_id, academic_year))
    #         if cursor.fetchone()[0] > 0:
    #             return {"success": False, "message": "Student already has an active assignment for this academic year."}

    #         # 2. Check route-stop consistency
    #         cursor.execute("SELECT COUNT(*) FROM BUS_STOP WHERE Stop_ID = ? AND Route_ID = ?", (stop_id, route_id))
    #         if cursor.fetchone()[0] == 0:
    #             return {"success": False, "message": "Selected stop does not belong to the selected route."}

    #         # 3. Check bus capacity
    #         cursor.execute("SELECT Capacity FROM BUS WHERE Bus_ID = ?", (bus_id,))
    #         bus_row = cursor.fetchone()
    #         if not bus_row:
    #             return {"success": False, "message": "Invalid Bus ID."}
    #         capacity = bus_row[0]

    #         cursor.execute("""
    #             SELECT COUNT(*) FROM TRANSPORT_ASSIGNMENT 
    #             WHERE Bus_ID = ? AND Academic_Year = ?
    #         """, (bus_id, academic_year))
    #         assigned = cursor.fetchone()[0]
    #         if assigned >= capacity:
    #             return {"success": False, "message": f"Selected bus (Bus ID: {bus_id}) is full ({assigned}/{capacity} seats)."}

    #         # 4. Generate next ID
    #         cursor.execute("SELECT IFNULL(MAX(Assignment_ID), 600) + 1 FROM TRANSPORT_ASSIGNMENT")
    #         new_id = cursor.fetchone()[0]

    #         # 5. Insert
    #         cursor.execute("""
    #             INSERT INTO TRANSPORT_ASSIGNMENT (Assignment_ID, Student_ID, Bus_ID, Route_ID, Stop_ID, Academic_Year, Assignment_Date)
    #             VALUES (?, ?, ?, ?, ?, ?, date('now'))
    #         """, (new_id, student_id, bus_id, route_id, stop_id, academic_year))
    #         conn.commit()

    #         return {
    #             "success": True, 
    #             "assignment_id": new_id, 
    #             "message": f"Successfully allocated student! Generated Assignment ID: {new_id}"
    #         }
    #     except Exception as e:
    #         conn.rollback()
    #         return {"success": False, "message": f"Database exception: {str(e)}"}
    #     finally:
    #         conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
    res = db.execute_query("SELECT count(*) FROM STUDENT;")
    print("Self-test:", res)

