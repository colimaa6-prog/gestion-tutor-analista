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
            # Admin ve a sus supervisados Y a sí mismo
            cursor.execute(
                "SELECT id FROM users WHERE supervisor_id = %s",
                (user_id,)
            )
            supervised = cursor.fetchall()
            supervised_ids = [row['id'] for row in supervised]
            # Incluir al admin mismo en la lista
            supervised_ids.append(user_id)
            return supervised_ids
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



# ==================== API: DASHBOARD DETAILS ====================

def get_dashboard_daily_detail(status):
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({'success': False, 'message': 'userId requerido'}), 400
    
    authorized_ids = get_authorized_user_ids(int(user_id))
    if not authorized_ids:
        return jsonify({'success': True, 'data': []})
        
    placeholders = ','.join(['%s' for _ in authorized_ids])
    
    # Adjust for Mexico time (UTC-6)
    from datetime import timedelta
    today = (datetime.utcnow() - timedelta(hours=6)).date()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            SELECT e.id, e.full_name, b.name as branch_name, a.comment
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            LEFT JOIN branches b ON e.branch_id = b.id
            JOIN attendance_roster ar ON e.id = ar.employee_id
            WHERE a.date = %s 
            AND a.status = %s 
            AND ar.added_by_user_id IN ({placeholders})
            ORDER BY e.full_name ASC
        """, [today, status] + authorized_ids)
        
        data = []
        for row in cursor.fetchall():
            data.append(dict_from_row(row))
            
        return jsonify({'success': True, 'data': data})
    finally:
        conn.close()

def get_dashboard_range_detail(status):
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({'success': False, 'message': 'userId requerido'}), 400
    
    authorized_ids = get_authorized_user_ids(int(user_id))
    if not authorized_ids:
        return jsonify({'success': True, 'data': []})
        
    placeholders = ','.join(['%s' for _ in authorized_ids])
    
    # Adjust for Mexico time (UTC-6)
    from datetime import timedelta
    today = (datetime.utcnow() - timedelta(hours=6)).date()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            SELECT e.id, e.full_name, b.name as branch_name, a.start_date, a.end_date, a.comment, a.permission_type
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            LEFT JOIN branches b ON e.branch_id = b.id
            JOIN attendance_roster ar ON e.id = ar.employee_id
            WHERE a.status = %s 
            AND a.start_date <= %s 
            AND a.end_date >= %s
            AND ar.added_by_user_id IN ({placeholders})
            ORDER BY e.full_name ASC
        """, [status, today, today] + authorized_ids)
        
        data = []
        for row in cursor.fetchall():
            item = dict_from_row(row)
            # Format dates
            if item.get('start_date'):
                item['start_date'] = item['start_date'].isoformat() if hasattr(item['start_date'], 'isoformat') else str(item['start_date'])
            if item.get('end_date'):
                item['end_date'] = item['end_date'].isoformat() if hasattr(item['end_date'], 'isoformat') else str(item['end_date'])
            data.append(item)
            
        return jsonify({'success': True, 'data': data})
    finally:
        conn.close()

@app.route('/api/dashboard/stats', methods=['GET', 'OPTIONS'])
def dashboard_stats():
    if request.method == 'OPTIONS':
        return '', 204
        
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({'success': False, 'message': 'userId requerido'}), 400
    
    authorized_ids = get_authorized_user_ids(int(user_id))
    if not authorized_ids:
        return jsonify({'success': True, 'data': {
            'asistencias': 0,
            'faltas': 0,
            'vacaciones': 0,
            'permisos': 0,
            'incapacidades': 0,
            'incidencias_activas': 0
        }})
    
    placeholders = ','.join(['%s' for _ in authorized_ids])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get today's date adjusted for Mexico time (UTC-6)
        from datetime import timedelta
        today = (datetime.utcnow() - timedelta(hours=6)).date()
        
        # Count attendances by status for today
        cursor.execute(f"""
            SELECT status, COUNT(*) as count
            FROM attendance
            WHERE date = %s
            AND employee_id IN (
                SELECT employee_id FROM attendance_roster
                WHERE added_by_user_id IN ({placeholders})
            )
            GROUP BY status
        """, [today] + authorized_ids)
        
        stats = {
            'asistencias': 0,
            'faltas': 0,
            'vacaciones': 0,
            'permisos': 0,
            'incapacidades': 0,
            'incidencias_activas': 0
        }
        
        for row in cursor:
            status = row['status']
            count = row['count']
            
            if status == 'present':
                stats['asistencias'] = count
            elif status == 'absent':
                stats['faltas'] = count
            elif status == 'vacation':
                stats['vacaciones'] = count
            elif status == 'permission':
                stats['permisos'] = count
            elif status == 'incapacity':
                stats['incapacidades'] = count
        
        # Count active incidents (simplified query to match /api/incidents logic)
        cursor.execute(f"""
            SELECT COUNT(*) as count
            FROM incidents
            WHERE status IN ('pending', 'in_progress', 'EN PROCESO')
            AND reported_by IN ({placeholders})
        """, authorized_ids)
        result = cursor.fetchone()
        if result:
            stats['incidencias_activas'] = result['count']
        
        return jsonify({'success': True, 'data': stats})
    finally:
        conn.close()

@app.route('/api/dashboard/absences', methods=['GET', 'OPTIONS'])
def dashboard_absences():
    if request.method == 'OPTIONS': return '', 204
    return get_dashboard_daily_detail('absent')

@app.route('/api/dashboard/vacations', methods=['GET', 'OPTIONS'])
def dashboard_vacations():
    if request.method == 'OPTIONS': return '', 204
    return get_dashboard_range_detail('vacation')

@app.route('/api/dashboard/permissions', methods=['GET', 'OPTIONS'])
def dashboard_permissions():
    if request.method == 'OPTIONS': return '', 204
    return get_dashboard_range_detail('permission')

@app.route('/api/dashboard/sick-leaves', methods=['GET', 'OPTIONS'])
def dashboard_sick_leaves():
    if request.method == 'OPTIONS': return '', 204
    return get_dashboard_range_detail('incapacity')

@app.route('/api/dashboard/active-incidents', methods=['GET', 'OPTIONS'])
def dashboard_active_incidents():
    if request.method == 'OPTIONS': return '', 204
    
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({'success': False, 'message': 'userId requerido'}), 400
    
    authorized_ids = get_authorized_user_ids(int(user_id))
    if not authorized_ids:
        return jsonify({'success': True, 'data': []})
        
    placeholders = ','.join(['%s' for _ in authorized_ids])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            SELECT i.*, u.username as reported_by_name, b.name as branch_name
            FROM incidents i
            JOIN users u ON i.reported_by = u.id
            LEFT JOIN branches b ON i.branch_id = b.id
            WHERE i.status IN ('pending', 'in_progress', 'EN PROCESO')
            AND i.reported_by IN ({placeholders})
            ORDER BY i.created_at DESC
        """, authorized_ids)
        
        data = []
        for row in cursor.fetchall():
            item = dict(row)
            for k, v in item.items():
                if hasattr(v, 'isoformat'):
                    item[k] = v.isoformat()
            data.append(item)
            
        return jsonify({'success': True, 'data': data})
    finally:
        conn.close()

@app.route('/api/incidents', methods=['GET', 'POST', 'OPTIONS'])
def incidents_list():
    if request.method == 'OPTIONS': 
        return '', 204
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if request.method == 'GET':
            cursor.execute("""
                SELECT i.*, e.full_name as reported_by_name, b.name as branch_name 
                FROM incidents i
                JOIN employees e ON i.reported_by = e.id
                LEFT JOIN branches b ON i.branch_id = b.id
                ORDER BY i.created_at DESC
            """)
            data = []
            for row in cursor.fetchall():
                item = dict(row)
                for k, v in item.items():
                    if hasattr(v, 'isoformat'):
                        item[k] = v.isoformat()
                data.append(item)
            return jsonify({'success': True, 'data': data})
        
        elif request.method == 'POST':
            data = request.json
            
            # Convertir cadenas vacías a None para campos de fecha
            start_date = data.get('start_date') or None
            end_date = data.get('end_date') or None
            branch_id = data.get('branch_id') or None
            reported_by = data.get('reported_by') or None
            
            cursor.execute("""
                INSERT INTO incidents 
                (branch_id, reported_by, type, status, description, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                branch_id,
                reported_by,
                data.get('type'),
                data.get('status', 'pending'),
                data.get('description'),
                start_date,
                end_date
            ))
            conn.commit()
            return jsonify({'success': True, 'message': 'Incidencia creada'})
    finally:
        conn.close()

@app.route('/api/incidents/<int:id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def incident_detail(id):
    if request.method == 'OPTIONS':
        return '', 204
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if request.method == 'DELETE':
            cursor.execute("DELETE FROM incidents WHERE id = %s", (id,))
            conn.commit()
            return jsonify({'success': True, 'message': 'Incidencia eliminada'})
            
        elif request.method == 'PUT':
            data = request.json
            print(f"PUT /api/incidents/{id} - Received data: {data}")
            
            # Convert empty strings to None for date fields
            start_date = data.get('start_date') or None
            end_date = data.get('end_date') or None
            
            # Frontend sends 'employee_id' but we need 'reported_by'
            # Also handle 'branch_id' which may not be sent
            reported_by = data.get('reported_by') or data.get('employee_id') or None
            branch_id = data.get('branch_id') or None
            
            print(f"Parsed values - branch_id: {branch_id}, reported_by: {reported_by}, type: {data.get('type')}, status: {data.get('status')}")
            
            cursor.execute("""
                UPDATE incidents 
                SET branch_id = %s,
                    reported_by = %s,
                    type = %s,
                    status = %s,
                    description = %s,
                    start_date = %s,
                    end_date = %s
                WHERE id = %s
            """, (
                branch_id,
                reported_by,
                data.get('type'),
                data.get('status'),
                data.get('description'),
                start_date,
                end_date,
                id
            ))
            conn.commit()
            print(f"Successfully updated incident {id}")
            return jsonify({'success': True, 'message': 'Incidencia actualizada'})
    except Exception as e:
        print(f"Error in incident_detail: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

# ==================== API: SUPERVISED TUTORS ====================

@app.route('/api/supervised-tutors', methods=['GET', 'OPTIONS'])
def get_supervised_tutors():
    if request.method == 'OPTIONS':
        return '', 204
        
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({'success': False, 'message': 'userId requerido'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get user role
        cursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({'success': True, 'tutors': []})
        
        # Get supervised tutors
        cursor.execute("""
            SELECT id, username, role
            FROM users
            WHERE supervisor_id = %s AND role = 'tutor_analista'
            ORDER BY username ASC
        """, (user_id,))
        
        tutors = []
        for row in cursor:
            tutors.append({
                'id': row['id'],
                'username': row['username'],
                'role': row['role']
            })
        
        return jsonify({'success': True, 'tutors': tutors})
    finally:
        conn.close()

# ==================== API: BRANCHES ====================

@app.route('/api/branches', methods=['GET', 'OPTIONS'])
def get_branches():
    if request.method == 'OPTIONS':
        return '', 204
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM branches ORDER BY name ASC")
        data = [dict(row) for row in cursor.fetchall()]
        return jsonify({'success': True, 'data': data})
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
                SELECT e.id, e.full_name, e.branch_id, e.hire_date, b.name as branch_name, e.status
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
                    'hire_date': row['hire_date'].isoformat() if row['hire_date'] and hasattr(row['hire_date'], 'isoformat') else row['hire_date'],
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
            
            # Obtener roster (empleados en la lista de asistencia)
            # Tutores ven solo lo que ellos agregan
            # Admins ven solo lo que sus tutores supervisados agregan
            cursor.execute(f"""
                SELECT DISTINCT e.id, e.full_name, e.branch_id, b.name as branch_name
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
                    'branch_name': row['branch_name'],
                    'marks': {}  # Will be populated with attendance records
                })
            
            if not employees:
                return jsonify({'success': True, 'data': []})
            
            # Obtener todos los registros de asistencia para estos empleados
            employee_ids = [emp['id'] for emp in employees]
            emp_placeholders = ','.join(['%s' for _ in employee_ids])
            
            cursor.execute(f"""
                SELECT a.employee_id, a.date, a.status, a.comment,
                       a.arrival_time, a.permission_type, a.start_date, a.end_date
                FROM attendance a
                WHERE a.employee_id IN ({emp_placeholders})
                ORDER BY a.date DESC
            """, employee_ids)
            
            # Organizar las marcas por empleado y fecha
            for row in cursor:
                emp_id = row['employee_id']
                date_str = row['date'].isoformat() if hasattr(row['date'], 'isoformat') else str(row['date'])
                
                # Encontrar el empleado correspondiente
                for emp in employees:
                    if emp['id'] == emp_id:
                        emp['marks'][date_str] = {
                            'status': row['status'],
                            'comment': row['comment'],
                            'arrival_time': row['arrival_time'],
                            'permission_type': row['permission_type'],
                            'start_date': row['start_date'].isoformat() if row['start_date'] and hasattr(row['start_date'], 'isoformat') else row['start_date'],
                            'end_date': row['end_date'].isoformat() if row['end_date'] and hasattr(row['end_date'], 'isoformat') else row['end_date']
                        }
                        break
            
            return jsonify({
                'success': True,
                'data': employees
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
            INSERT INTO attendance_roster (employee_id, added_by_user_id)
            VALUES (%s, %s)
            ON CONFLICT (employee_id) DO NOTHING
        """, (employee_id, user_id))
        conn.commit()
        
        return jsonify({'success': True})
    finally:
        conn.close()

@app.route('/api/attendance/roster/<int:employee_id>', methods=['DELETE', 'OPTIONS'])
def delete_from_roster(employee_id):
    if request.method == 'OPTIONS':
        return '', 204
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM attendance_roster 
            WHERE employee_id = %s
        """, (employee_id,))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Colaborador eliminado del roster'})
    finally:
        conn.close()

@app.route('/api/attendance/mark', methods=['POST', 'OPTIONS'])
def mark_attendance():
    if request.method == 'OPTIONS':
        return '', 204
        
    data = request.json
    employee_id = data.get('employee_id')
    date = data.get('date')
    status = data.get('status')
    comment = data.get('comment', '')
    arrival_time = data.get('arrival_time', '')
    permission_type = data.get('permission_type', '')
    start_date = data.get('start_date') or None
    end_date = data.get('end_date') or None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if status == 'none':
            # Delete the attendance record
            cursor.execute("""
                DELETE FROM attendance 
                WHERE employee_id = %s AND date = %s
            """, (employee_id, date))
        else:
            # Insert or update attendance record with all fields
            cursor.execute("""
                INSERT INTO attendance (employee_id, date, status, comment, arrival_time, permission_type, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (employee_id, date)
                DO UPDATE SET 
                    status = EXCLUDED.status,
                    comment = EXCLUDED.comment,
                    arrival_time = EXCLUDED.arrival_time,
                    permission_type = EXCLUDED.permission_type,
                    start_date = EXCLUDED.start_date,
                    end_date = EXCLUDED.end_date
            """, (employee_id, date, status, comment, arrival_time, permission_type, start_date, end_date))
        
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
            
            month = request.args.get('month', 0)
            year = request.args.get('year', 2026)
            
            placeholders = ','.join(['%s' for _ in authorized_ids])
            
            # Obtener empleados del roster con sus datos de reportes
            # Tutores ven solo lo que ellos agregan
            # Admins ven solo lo que sus tutores supervisados agregan
            cursor.execute(f"""
                SELECT DISTINCT 
                    e.id, 
                    e.full_name, 
                    e.branch_id, 
                    b.name as branch_name,
                    r.data as report_data
                FROM attendance_roster ar
                JOIN employees e ON ar.employee_id = e.id
                LEFT JOIN branches b ON e.branch_id = b.id
                LEFT JOIN reports r ON r.employee_id = e.id 
                    AND r.month = %s AND r.year = %s
                WHERE ar.added_by_user_id IN ({placeholders})
                ORDER BY e.full_name ASC
            """, [month, year] + authorized_ids)
            
            employees = []
            for row in cursor:
                employees.append({
                    'id': row['id'],
                    'full_name': row['full_name'],
                    'branch_id': row['branch_id'],
                    'branch_name': row['branch_name'],
                    'report_data': row['report_data']  # Include report data
                })
            
            return jsonify({
                'success': True,
                'employees': employees
            })
        
        
        elif request.method == 'POST':
            data = request.json
            
            # Check if this is a full data update or incremental update
            if 'data' in data:
                # Full data update (old format)
                report_data = json.dumps(data.get('data'))
                employee_id = data.get('employee_id')
                month = data.get('month')
                year = data.get('year')
            else:
                # Incremental update (new format from frontend)
                employee_id = data.get('employee_id')
                month = data.get('month')
                year = data.get('year')
                update_type = data.get('type')  # 'faltantes', 'guias', 'tableros'
                key = data.get('key')  # day number or quincena/semana number
                status = data.get('status')
                comment = data.get('comment', '')
                
                # Fetch existing report data
                cursor.execute("""
                    SELECT data FROM reports 
                    WHERE employee_id = %s AND month = %s AND year = %s
                """, (employee_id, month, year))
                
                existing = cursor.fetchone()
                if existing and existing['data'] and existing['data'].strip():
                    try:
                        report_obj = json.loads(existing['data'])
                    except (json.JSONDecodeError, TypeError):
                        report_obj = {'faltantes': {}, 'guias': {}, 'tableros': {}}
                else:
                    report_obj = {'faltantes': {}, 'guias': {}, 'tableros': {}}
                
                # Ensure report_obj is a dict
                if not isinstance(report_obj, dict):
                    report_obj = {'faltantes': {}, 'guias': {}, 'tableros': {}}
                
                # Update the specific field
                if update_type not in report_obj:
                    report_obj[update_type] = {}
                
                if status == 'empty':
                    # Remove the entry
                    if str(key) in report_obj[update_type]:
                        del report_obj[update_type][str(key)]
                else:
                    report_obj[update_type][str(key)] = {
                        'status': status,
                        'comment': comment
                    }
                
                report_data = json.dumps(report_obj)
            
            cursor.execute("""
                INSERT INTO reports (employee_id, month, year, data)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (employee_id, month, year) 
                DO UPDATE SET data = EXCLUDED.data
            """, (employee_id, month, year, report_data))
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

