"""
SCHOOL BUS ROUTE AND STUDENT TRANSPORT MANAGEMENT SYSTEM
Application Interface & Interactive SQL Query Runner
Built with Python standard library http.server (Zero external dependencies)
"""

import http.server
import json
import os
import sys
import urllib.parse
import webbrowser
from db_connection import DatabaseManager

PORT = 5000
db = DatabaseManager()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>School Bus Transport Management System | DBMS Interface</title>
    <style>
        :root {
            --primary: #1e3a8a;
            --primary-light: #3b82f6;
            --secondary: #0f766e;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --success: #15803d;
            --danger: #b91c1c;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
        body { background: var(--bg); color: var(--text); padding-bottom: 60px; }
        header { background: linear-gradient(135deg, #1e3a8a 0%, #0f766e 100%); color: white; padding: 24px 32px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .header-content h1 { font-size: 24px; font-weight: 700; }
        .header-content p { font-size: 14px; opacity: 0.9; margin-top: 4px; }
        .badge-live { background: rgba(34, 197, 94, 0.2); border: 1px solid #4ade80; color: #dcfce7; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
        .badge-dot { width: 8px; height: 8px; background: #22c55e; border-radius: 50%; display: inline-block; }

        .container { max-width: 1200px; margin: 24px auto; padding: 0 20px; }
        .nav-tabs { display: flex; gap: 12px; border-bottom: 2px solid var(--border); margin-bottom: 24px; }
        .tab-btn { background: none; border: none; padding: 12px 20px; font-size: 15px; font-weight: 600; color: var(--text-muted); cursor: pointer; border-bottom: 3px solid transparent; transition: all 0.2s; }
        .tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); }
        .tab-btn:hover:not(.active) { color: var(--text); }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        .card { background: var(--card-bg); border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 1px 3px rgba(0,0,0,0.05); padding: 24px; margin-bottom: 24px; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
        .card-title { font-size: 18px; font-weight: 700; color: var(--primary); }

        /* SQL Terminal */
        .sql-box { width: 100%; min-height: 140px; padding: 14px; font-family: 'Consolas', 'Courier New', monospace; font-size: 14px; border: 1px solid var(--border); border-radius: 8px; background: #0f172a; color: #f8fafc; resize: vertical; line-height: 1.5; }
        .presets { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 16px; }
        .preset-btn { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: 500; cursor: pointer; transition: 0.15s; }
        .preset-btn:hover { background: #bae6fd; }

        .btn-run { background: var(--primary); color: white; border: none; padding: 10px 24px; border-radius: 6px; font-size: 15px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: 0.15s; }
        .btn-run:hover { background: #1d4ed8; }

        /* Results Display */
        .stats-badge { display: inline-block; padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: 600; margin-bottom: 12px; }
        .stats-success { background: #dcfce7; color: var(--success); }
        .stats-error { background: #fee2e2; color: var(--danger); }

        .table-responsive { width: 100%; overflow-x: auto; border: 1px solid var(--border); border-radius: 8px; margin-top: 12px; }
        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }
        th { background: #f1f5f9; color: var(--primary); font-weight: 700; padding: 12px 14px; border-bottom: 2px solid var(--border); white-space: nowrap; }
        td { padding: 10px 14px; border-bottom: 1px solid var(--border); white-space: nowrap; }
        tr:hover td { background: #f8fafc; }

        /* Form Controls */
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 16px; }
        .form-group { display: flex; flex-direction: column; gap: 6px; }
        .form-group label { font-size: 13px; font-weight: 600; color: var(--text-muted); }
        .form-group select, .form-group input { padding: 9px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px; background: white; }

        .table-picker { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
        .table-btn { background: #f1f5f9; border: 1px solid var(--border); padding: 8px 14px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 13px; }
        .table-btn.active { background: var(--primary); color: white; border-color: var(--primary); }
    </style>
</head>
<body>

<header>
    <div class="header-content">
        <div>
            <h1>School Bus Route & Student Transport Management System</h1>
            <p>DBMS Project-Based Learning (PBL) Interactive Application Interface</p>
        </div>
        <div class="badge-live">
            <span class="badge-dot"></span> MySQL 8.0 Connected
        </div>
    </div>
</header>

<div class="container">
    <div class="nav-tabs">
        <button class="tab-btn active" onclick="switchTab('query-tab')">⚡ Interface for Firing SQL Queries</button>
        <button class="tab-btn" onclick="switchTab('allocation-tab')">📝 Student Transport Allocation</button>
        <button class="tab-btn" onclick="switchTab('explorer-tab')">📊 Database Tables & Views Explorer</button>
    </div>

    <!-- TAB 1: SQL QUERY RUNNER -->
    <div id="query-tab" class="tab-content active">
        <div class="card">
            <div class="card-header">
                <span class="card-title">Interactive SQL Query Terminal</span>
                <span style="font-size: 13px; color: var(--text-muted);">Execute arbitrary SELECT, JOIN, TRIGGER, or PROCEDURE calls</span>
            </div>

            <div class="presets">
                <span style="font-size: 13px; font-weight: 600; align-self: center;">Quick Presets:</span>
                <button class="preset-btn" onclick="setQuery('SELECT * FROM vw_student_transport_details LIMIT 10;')">7-Table Master Manifest</button>
                <button class="preset-btn" onclick="setQuery('CALL sp_get_bus_utilization_report();')">Procedure: Fleet Utilization</button>
                <button class="preset-btn" onclick="setQuery('CALL sp_get_route_student_manifest(401);')">Procedure: Route 401 Manifest</button>
                <button class="preset-btn" onclick="setQuery('SELECT * FROM vw_route_operational_summary;')">View: Route Summary</button>
                <button class="preset-btn" onclick="setQuery('SELECT * FROM ASSIGNMENT_AUDIT_LOG ORDER BY Log_ID DESC;')">Audit Log Table</button>
                <button class="preset-btn" onclick="setQuery('INSERT INTO TRANSPORT_ASSIGNMENT (Assignment_ID, Student_ID, Bus_ID, Route_ID, Stop_ID, Academic_Year, Assignment_Date) VALUES (999, 1001, 301, 401, 509, \\'2029-2030\\', CURDATE());')">Test Trigger (Mismatch Error)</button>
            </div>

            <textarea id="sqlInput" class="sql-box" placeholder="Enter your SQL query here (e.g., SELECT * FROM STUDENT;)">SELECT * FROM vw_student_transport_details;</textarea>
            
            <div style="margin-top: 14px; display: flex; justify-content: space-between; align-items: center;">
                <button class="btn-run" onclick="runQuery()">▶ Execute SQL Query</button>
                <span id="execStats" style="font-size: 13px; color: var(--text-muted);"></span>
            </div>
        </div>

        <div id="resultCard" class="card" style="display: none;">
            <div class="card-header">
                <span class="card-title">Execution Results</span>
            </div>
            <div id="statusBadge"></div>
            <div id="tableContainer" class="table-responsive"></div>
        </div>
    </div>

    <!-- TAB 2: ALLOCATION FORM -->
    <div id="allocation-tab" class="tab-content">
        <div class="card">
            <div class="card-header">
                <span class="card-title">New Student Transport Allocation Form</span>
                <span style="font-size: 13px; color: var(--text-muted);">Invokes stored procedure & verifies bus capacity</span>
            </div>
            <form id="allocForm" onsubmit="submitAllocation(event)">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Student</label>
                        <select id="selStudent" required></select>
                    </div>
                    <div class="form-group">
                        <label>Bus</label>
                        <select id="selBus" required></select>
                    </div>
                    <div class="form-group">
                        <label>Route</label>
                        <select id="selRoute" onchange="loadStopsForRoute(this.value)" required></select>
                    </div>
                    <div class="form-group">
                        <label>Designated Pickup Stop</label>
                        <select id="selStop" required></select>
                    </div>
                    <div class="form-group">
                        <label>Academic Year</label>
                        <input type="text" id="inpYear" value="2027-2028" required>
                    </div>
                </div>
                <button type="submit" class="btn-run">Assign Student Transport</button>
            </form>
            <div id="allocResult" style="margin-top: 16px;"></div>
        </div>
    </div>

    <!-- TAB 3: EXPLORER -->
    <div id="explorer-tab" class="tab-content">
        <div class="card">
            <div class="card-header">
                <span class="card-title">Database Tables & Views Explorer</span>
            </div>
            <div class="table-picker">
                <button class="table-btn active" onclick="loadExplorerTable('STUDENT', this)">STUDENT</button>
                <button class="table-btn" onclick="loadExplorerTable('PARENT', this)">PARENT</button>
                <button class="table-btn" onclick="loadExplorerTable('DRIVER', this)">DRIVER</button>
                <button class="table-btn" onclick="loadExplorerTable('BUS', this)">BUS</button>
                <button class="table-btn" onclick="loadExplorerTable('ROUTE', this)">ROUTE</button>
                <button class="table-btn" onclick="loadExplorerTable('BUS_STOP', this)">BUS_STOP</button>
                <button class="table-btn" onclick="loadExplorerTable('TRANSPORT_ASSIGNMENT', this)">TRANSPORT_ASSIGNMENT</button>
                <button class="table-btn" onclick="loadExplorerTable('ASSIGNMENT_AUDIT_LOG', this)">AUDIT_LOG</button>
                <button class="table-btn" onclick="loadExplorerTable('vw_bus_occupancy_summary', this)">Occupancy View</button>
            </div>
            <div id="explorerResult" class="table-responsive"></div>
        </div>
    </div>
</div>

<script>
    function switchTab(tabId) {
        document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        event.currentTarget.classList.add('active');
        if (tabId === 'allocation-tab') loadFormOptions();
        if (tabId === 'explorer-tab') loadExplorerTable('STUDENT', document.querySelector('.table-btn'));
    }

    function setQuery(sql) {
        document.getElementById('sqlInput').value = sql;
    }

    async function runQuery() {
        const sql = document.getElementById('sqlInput').value.trim();
        if (!sql) return;

        const resCard = document.getElementById('resultCard');
        const badge = document.getElementById('statusBadge');
        const tblContainer = document.getElementById('tableContainer');
        const execStats = document.getElementById('execStats');

        resCard.style.display = 'block';
        badge.innerHTML = '<span class="stats-badge" style="background:#e0f2fe; color:#0369a1;">Executing query...</span>';
        tblContainer.innerHTML = '';

        try {
            const resp = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: sql })
            });
            const data = await resp.json();

            if (data.success) {
                badge.innerHTML = `<span class="stats-badge stats-success">${data.message}</span>`;
                execStats.innerText = `Latency: ${data.execution_time_ms} ms`;

                if (data.is_select && data.rows.length > 0) {
                    let html = '<table><thead><tr>';
                    data.columns.forEach(col => html += `<th>${col}</th>`);
                    html += '</tr></thead><tbody>';
                    data.rows.forEach(row => {
                        html += '<tr>';
                        row.forEach(val => html += `<td>${val !== null ? val : '<em>NULL</em>'}</td>`);
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                    tblContainer.innerHTML = html;
                } else if (data.is_select) {
                    tblContainer.innerHTML = '<p style="padding: 16px; color: var(--text-muted);">Query executed successfully. 0 rows returned.</p>';
                } else {
                    tblContainer.innerHTML = `<p style="padding: 16px; color: var(--success); font-weight: 600;">Success: ${data.affected_rows} row(s) affected.</p>`;
                }
            } else {
                badge.innerHTML = `<span class="stats-badge stats-error">Execution Error</span>`;
                execStats.innerText = '';
                tblContainer.innerHTML = `<div style="padding:16px; background:#fff1f2; border:1px solid #fecdd3; border-radius:6px; color:#9f1239; font-family:monospace;">${data.error}</div>`;
            }
        } catch (err) {
            badge.innerHTML = `<span class="stats-badge stats-error">Network / Server Error: ${err}</span>`;
        }
    }

    async function loadExplorerTable(tableName, btn) {
        document.querySelectorAll('.table-btn').forEach(b => b.classList.remove('active'));
        if (btn) btn.classList.add('active');
        const container = document.getElementById('explorerResult');
        container.innerHTML = '<p style="padding:16px;">Loading...</p>';

        const resp = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: `SELECT * FROM ${tableName} LIMIT 50;` })
        });
        const data = await resp.json();
        if (data.success && data.rows.length > 0) {
            let html = '<table><thead><tr>';
            data.columns.forEach(c => html += `<th>${c}</th>`);
            html += '</tr></thead><tbody>';
            data.rows.forEach(r => {
                html += '<tr>';
                r.forEach(v => html += `<td>${v !== null ? v : '<em>NULL</em>'}</td>`);
                html += '</tr>';
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p style="padding:16px;">No records found.</p>';
        }
    }

    async function loadFormOptions() {
        const resp = await fetch('/api/options');
        const data = await resp.json();

        const selStudent = document.getElementById('selStudent');
        selStudent.innerHTML = data.students.map(s => `<option value="${s.Student_ID}">${s.Student_ID} - ${s.Student_Name} (${s.Class}-${s.Section})</option>`).join('');

        const selBus = document.getElementById('selBus');
        selBus.innerHTML = data.buses.map(b => `<option value="${b.Bus_ID}">${b.Bus_Number} - ${b.Bus_Model} (Cap: ${b.Capacity})</option>`).join('');

        const selRoute = document.getElementById('selRoute');
        selRoute.innerHTML = data.routes.map(r => `<option value="${r.Route_ID}">${r.Route_ID} - ${r.Route_Name}</option>`).join('');

        if (data.routes.length > 0) {
            loadStopsForRoute(data.routes[0].Route_ID);
        }
    }

    async function loadStopsForRoute(routeId) {
        const resp = await fetch(`/api/stops?route_id=${routeId}`);
        const stops = await resp.json();
        const selStop = document.getElementById('selStop');
        selStop.innerHTML = stops.map(s => `<option value="${s.Stop_ID}">Stop ${s.Stop_Order}: ${s.Stop_Name} (${s.Location})</option>`).join('');
    }

    async function submitAllocation(e) {
        e.preventDefault();
        const sId = document.getElementById('selStudent').value;
        const bId = document.getElementById('selBus').value;
        const rId = document.getElementById('selRoute').value;
        const stId = document.getElementById('selStop').value;
        const year = document.getElementById('inpYear').value;

        const resDiv = document.getElementById('allocResult');
        resDiv.innerHTML = '<span class="stats-badge" style="background:#e0f2fe; color:#0369a1;">Processing allocation...</span>';

        const resp = await fetch('/api/allocate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: sId, bus_id: bId, route_id: rId, stop_id: stId, academic_year: year })
        });
        const result = await resp.json();
        if (result.success) {
            resDiv.innerHTML = `<div style="padding:14px; background:#dcfce7; border:1px solid #86efac; border-radius:6px; color:#15803d; font-weight:600;">${result.message}</div>`;
        } else {
            resDiv.innerHTML = `<div style="padding:14px; background:#fee2e2; border:1px solid #fca5a5; border-radius:6px; color:#b91c1c; font-weight:600;">${result.message}</div>`;
        }
    }
</script>

</body>
</html>
"""

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))

        elif path == "/api/options":
            students = db.execute_query("SELECT Student_ID, Student_Name, Class, Section FROM STUDENT ORDER BY Student_ID;")["rows"]
            buses = db.execute_query("SELECT Bus_ID, Bus_Number, Bus_Model, Capacity FROM BUS WHERE Status='Active';")["rows"]
            routes = db.execute_query("SELECT Route_ID, Route_Name FROM ROUTE ORDER BY Route_ID;")["rows"]

            payload = {
                "students": [{"Student_ID": r[0], "Student_Name": r[1], "Class": r[2], "Section": r[3]} for r in students],
                "buses": [{"Bus_ID": r[0], "Bus_Number": r[1], "Bus_Model": r[2], "Capacity": r[3]} for r in buses],
                "routes": [{"Route_ID": r[0], "Route_Name": r[1]} for r in routes]
            }
            self.send_json(payload)

        elif path == "/api/stops":
            query_params = urllib.parse.parse_qs(parsed.query)
            route_id = query_params.get("route_id", [None])[0]
            if route_id:
                res = db.execute_query(f"SELECT Stop_ID, Stop_Name, Location, Stop_Order FROM BUS_STOP WHERE Route_ID = {int(route_id)} ORDER BY Stop_Order;")
                stops = [{"Stop_ID": r[0], "Stop_Name": r[1], "Location": r[2], "Stop_Order": r[3]} for r in res["rows"]]
                self.send_json(stops)
            else:
                self.send_json([])
        else:
            self.send_error(404, "Endpoint Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        data = json.loads(body) if body else {}

        if parsed.path == "/api/query":
            sql = data.get("query", "")
            result = db.execute_query(sql)
            self.send_json(result)

        elif parsed.path == "/api/allocate":
            s_id = data.get("student_id")
            b_id = data.get("bus_id")
            r_id = data.get("route_id")
            st_id = data.get("stop_id")
            year = data.get("academic_year")

            call_sql = f"CALL sp_allocate_student_transport({s_id}, {b_id}, {r_id}, {st_id}, '{year}', @code, @msg);"
            res = db.execute_query(call_sql)
            if res["success"]:
                msg_res = db.execute_query("SELECT @code AS code, @msg AS msg;")
                if msg_res["success"] and msg_res["rows"]:
                    code = msg_res["rows"][0][0]
                    msg = msg_res["rows"][0][1]
                    self.send_json({"success": (code == 'SUCCESS'), "message": msg})
                else:
                    self.send_json({"success": True, "message": "Allocation executed successfully."})
            else:
                self.send_json({"success": False, "message": res.get("error", "Error executing stored procedure.")})
        else:
            self.send_error(404, "Endpoint Not Found")

    def send_json(self, payload):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload, default=str).encode("utf-8"))

def main():
    print("=" * 70)
    print("SCHOOL BUS TRANSPORT MANAGEMENT SYSTEM - APPLICATION INTERFACE")
    print("=" * 70)
    print(f"Starting server on http://127.0.0.1:{PORT}")
    print("Press Ctrl + C in terminal to stop the server.")
    print("Opening browser automatically...")
    
    webbrowser.open(f"http://127.0.0.1:{PORT}")
    server = http.server.HTTPServer(("127.0.0.1", PORT), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
        server.server_close()

if __name__ == "__main__":
    main()