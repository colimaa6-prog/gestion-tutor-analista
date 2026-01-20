
@app.route('/api/attendance/archived-months', methods=['GET', 'OPTIONS'])
def archived_months():
    if request.method == 'OPTIONS':
        return '', 204
    
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
        # Agrupar asistencias por mes y año para mostrar historial
        # Se filtra por usuarios autorizados
        cursor.execute(f"""
            SELECT 
                CAST(EXTRACT(MONTH FROM a.date) AS INTEGER) as month, 
                CAST(EXTRACT(YEAR FROM a.date) AS INTEGER) as year, 
                COUNT(*) as record_count
            FROM attendance a
            JOIN attendance_roster ar ON a.employee_id = ar.employee_id
            WHERE ar.added_by_user_id IN ({placeholders})
            GROUP BY year, month
            ORDER BY year DESC, month DESC
        """, authorized_ids)
        
        data = []
        for row in cursor.fetchall():
            data.append({
                'month': int(row['month']) - 1, # Ajustar a 0-indexed para JS (0=Enero)
                'year': int(row['year']),
                'record_count': row['record_count']
            })
            
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        print(f"Error en archived_months: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()
