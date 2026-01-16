from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__, static_folder='public', static_url_path='')

# Detectar si estamos en Railway (PostgreSQL) o local (SQLite)
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

# Debug: Mostrar qué base de datos se está usando
print(f"🔍 DATABASE_URL encontrada: {DATABASE_URL is not None}")
print(f"🔍 Usando {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")

# Ruta de la base de datos SQLite (solo para local)
DB_PATH = 'gestion_tutor.db'

def get_db_connection():
    """Crear conexión a PostgreSQL o SQLite según el entorno"""
    if USE_POSTGRES:
        # Conexión a PostgreSQL (Railway)
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.DictCursor)
        return conn
    else:
        # Conexión a SQLite (local)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def dict_from_row(row):
    """Convertir fila de DB a diccionario"""
    if USE_POSTGRES:
        return dict(row)
    else:
        return dict(row)

def get_authorized_user_ids(user_id):
    """Obtener IDs de usuarios autorizados según jerarquía"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener información del usuario
        cursor.execute(
            "SELECT id, role, supervisor_id FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            return []
        
        if user['role'] == 'admin':
            # Admin ve a sus supervisados
            cursor.execute(
                "SELECT id FROM users WHERE supervisor_id = %s",
                (user_id,)
            )
            supervised = cursor.fetchall()
            return [row['id'] for row in supervised]
        else:
            # Usuario regular solo se ve a sí mismo
            return [user_id]
    finally:
        conn.close()

# ==================== RUTAS ESTÁTICAS ====================

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('public', path)

# ==================== API: AUTH ====================

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204
        
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """SELECT id, username, role, branch_id 
               FROM users 
               WHERE username = %s AND password_hash = %s""",
            (username, password)
        )
        user = cursor.fetchone()
        
        if user:
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'role': user['role'],
                    'branch_id': user['branch_id']
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Credenciales inválidas'}), 401
    finally:
        conn.close()

# ==================== API: DASHBOARD ====================

@app.route('/api/dashboard/stats', methods=['GET', 'OPTIONS'])
def dashboard_stats():
    if request.method == 'OPTIONS':
        return '', 204
        
    user_id = request.args.get('userId')
    
    if not user_id:
        return jsonify({'success': False, 'message': 'userId requerido'}), 400
    
    authorized_ids = get_authorized_user_ids(int(user_id))
    
    if not authorized_ids:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        placeholders = ','.join(['%s' for _ in authorized_ids])
        
        # Total empleados en roster
        cursor.execute(f"""
            SELECT COUNT(DISTINCT ar.employee_id)
            FROM attendance_roster ar
            WHERE ar.added_by_user_id IN ({placeholders})
        """, authorized_ids)
        total_employees = cursor.fetchone()[0]
        
        # Incidencias activas
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM incidents i
            JOIN employees e ON i.reported_by = e.id
            JOIN attendance_roster ar ON e.id = ar.employee_id
            WHERE ar.added_by_user_id IN ({placeholders})
            AND i.status IN ('pending', 'in_progress')
        """, authorized_ids)
        active_incidents = cursor.fetchone()[0]
        
        # Asistencias del mes actual
        if USE_POSTGRES:
            cursor.execute(f"""
                SELECT COUNT(*)
                FROM attendance a
                JOIN attendance_roster ar ON a.employee_id = ar.employee_id
                WHERE ar.added_by_user_id IN ({placeholders})
                AND EXTRACT(MONTH FROM a.date) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM a.date) = EXTRACT(YEAR FROM CURRENT_DATE)
            """, authorized_ids)
        else:
            cursor.execute(f"""
                SELECT COUNT(*)
                FROM attendance a
                JOIN attendance_roster ar ON a.employee_id = ar.employee_id
                WHERE ar.added_by_user_id IN ({placeholders})
                AND strftime('%m', a.date) = strftime('%m', 'now')
                AND strftime('%Y', a.date) = strftime('%Y', 'now')
            """, authorized_ids)
        monthly_attendance = cursor.fetchone()[0]
        
        return jsonify({
            'success': True,
            'stats': {
                'totalEmployees': total_employees,
                'activeIncidents': active_incidents,
                'monthlyAttendance': monthly_attendance,
                'pendingReports': 0
            }
        })
    finally:
        conn.close()

# ==================== API: EMPLOYEES ====================

@app.route('/api/employees', methods=['GET', 'POST', 'OPTIONS'])
def employees():
    if request.method == 'OPTIONS':
        return '', 204
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if request.method == 'GET':
            cursor.execute("""
                SELECT e.id, e.full_name, e.branch_id, b.name as branch_name, e.status
                FROM employees e
                LEFT JOIN branches b ON e.branch_id = b.id
                ORDER BY e.full_name ASC
            """)
            
            employees = []
            for row in cursor:
                employees.append({
                    'id': row['id'],
                    'full_name': row['full_name'],
                    'branch_id': row['branch_id'],
                    'branch_name': row['branch_name'],
                    'status': row['status']
                })
            
            return jsonify({'success': True, 'data': employees})
        
        elif request.method == 'POST':
            data = request.json
            cursor.execute("""
                INSERT INTO employees (full_name, branch_id, status)
                VALUES (%s, %s, 'active')
            """, (data.get('full_name'), data.get('branch_id')))
            conn.commit()
            
            return jsonify({'success': True, 'message': 'Empleado creado'})
    finally:
        conn.close()

# ==================== API: ATTENDANCE ====================

@app.route('/api/attendance', methods=['GET', 'POST', 'OPTIONS'])
def attendance():
    if request.method == 'OPTIONS':
        return '', 204
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if request.method == 'GET':
            user_id = request.args.get('userId')
            
            if not user_id:
                return jsonify({'success': False, 'message': 'userId requerido'}), 400
            
            authorized_ids = get_authorized_user_ids(int(user_id))
            
            if not authorized_ids:
                return jsonify({'success': False, 'message': 'No autorizado'}), 403
            
            placeholders = ','.join(['%s' for _ in authorized_ids])
            
            # Obtener roster
            cursor.execute(f"""
                SELECT e.id, e.full_name, e.branch_id, b.name as branch_name
                FROM attendance_roster ar
                JOIN employees e ON ar.employee_id = e.id
                LEFT JOIN branches b ON e.branch_id = b.id
                WHERE ar.added_by_user_id IN ({placeholders})
                ORDER BY e.full_name ASC
            """, authorized_ids)
            
            roster = []
            for row in cursor:
                roster.append({
                    'id': row['id'],
                    'full_name': row['full_name'],
                    'branch_id': row['branch_id'],
                    'branch_name': row['branch_name']
                })
            
            # Obtener registros de asistencia
            cursor.execute(f"""
                SELECT a.id, a.employee_id, a.date, a.status, a.comment,
                       a.arrival_time, a.permission_type, a.start_date, a.end_date,
                       e.full_name
                FROM attendance a
                JOIN attendance_roster ar ON a.employee_id = ar.employee_id
                JOIN employees e ON a.employee_id = e.id
                WHERE ar.added_by_user_id IN ({placeholders})
                ORDER BY a.date DESC
            """, authorized_ids)
            
            records = []
            for row in cursor:
                records.append({
                    'id': row['id'],
                    'employee_id': row['employee_id'],
                    'date': row['date'],
                    'status': row['status'],
                    'comment': row['comment'],
                    'arrival_time': row['arrival_time'],
                    'permission_type': row['permission_type'],
                    'start_date': row['start_date'],
                    'end_date': row['end_date'],
                    'employee_name': row['full_name']
                })
            
            return jsonify({
                'success': True,
                'roster': roster,
                'records': records
            })
        
        elif request.method == 'POST':
            data = request.json
            cursor.execute("""
                INSERT INTO attendance 
                (employee_id, date, status, comment, arrival_time, 
                 permission_type, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get('employee_id'),
                data.get('date'),
                data.get('status'),
                data.get('comment'),
                data.get('arrival_time'),
                data.get('permission_type'),
                data.get('start_date'),
                data.get('end_date')
            ))
            conn.commit()
            
            return jsonify({'success': True})
    finally:
        conn.close()

@app.route('/api/attendance/roster', methods=['POST', 'OPTIONS'])
def add_to_roster():
    if request.method == 'OPTIONS':
        return '', 204
        
    data = request.json
    employee_id = data.get('employee_id')
    user_id = data.get('userId')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO attendance_roster (employee_id, added_by_user_id)
            VALUES (%s, %s)
        """, (employee_id, user_id))
        conn.commit()
        
        return jsonify({'success': True})
    finally:
        conn.close()

@app.route('/api/attendance/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_attendance(id):
    if request.method == 'OPTIONS':
        return '', 204
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM attendance WHERE id = %s", (id,))
        conn.commit()
        
        return jsonify({'success': True})
    finally:
        conn.close()

# ==================== API: REPORTS ====================

@app.route('/api/reports', methods=['GET', 'POST', 'OPTIONS'])
def reports():
    if request.method == 'OPTIONS':
        return '', 204
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if request.method == 'GET':
            user_id = request.args.get('userId')
            
            if not user_id:
                return jsonify({'success': False, 'message': 'userId requerido'}), 400
            
            authorized_ids = get_authorized_user_ids(int(user_id))
            
            if not authorized_ids:
                return jsonify({'success': False, 'message': 'No autorizado'}), 403
            
            placeholders = ','.join(['%s' for _ in authorized_ids])
            
            # Obtener empleados del roster
            cursor.execute(f"""
                SELECT e.id, e.full_name, e.branch_id, b.name as branch_name
                FROM attendance_roster ar
                JOIN employees e ON ar.employee_id = e.id
                LEFT JOIN branches b ON e.branch_id = b.id
                WHERE ar.added_by_user_id IN ({placeholders})
                ORDER BY e.full_name ASC
            """, authorized_ids)
            
            employees = []
            for row in cursor:
                employees.append({
                    'id': row['id'],
                    'full_name': row['full_name'],
                    'branch_id': row['branch_id'],
                    'branch_name': row['branch_name']
                })
            
            return jsonify({
                'success': True,
                'employees': employees
            })
        
        elif request.method == 'POST':
            data = request.json
            report_data = json.dumps(data.get('data'))
            
            cursor.execute("""
                INSERT OR REPLACE INTO reports (employee_id, month, year, data)
                VALUES (%s, %s, %s, %s)
            """, (
                data.get('employee_id'),
                data.get('month'),
                data.get('year'),
                report_data
            ))
            conn.commit()
            
            return jsonify({'success': True})
    finally:
        conn.close()

@app.route('/api/reports/data', methods=['GET', 'OPTIONS'])
def get_report_data():
    if request.method == 'OPTIONS':
        return '', 204
        
    employee_id = request.args.get('employeeId')
    month = request.args.get('month')
    year = request.args.get('year')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT data FROM reports
            WHERE employee_id = %s AND month = %s AND year = %s
        """, (employee_id, month, year))
        
        result = cursor.fetchone()
        
        if result and result['data']:
            data = json.loads(result['data'])
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'success': True, 'data': None})
    finally:
        conn.close()

# ==================== CORS Headers ====================

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ==================== MAIN ====================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)

