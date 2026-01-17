# Plan de Implementación: Sistema de Asignación de Tutores para Administradores

## Objetivo
Permitir que los administradores puedan crear, editar y eliminar información asignándola a sus tutores supervisados.

## Estado Actual
✅ Endpoint `/api/supervised-tutors` creado - Devuelve lista de tutores supervisados por un admin

## Cambios Necesarios

### 1. BACKEND - Modificar Endpoints

#### A. Endpoint: POST /api/attendance/roster (Agregar colaborador)
```python
@app.route('/api/attendance/roster', methods=['POST', 'OPTIONS'])
def add_to_roster():
    if request.method == 'OPTIONS':
        return '', 204
        
    data = request.json
    employee_id = data.get('employee_id')
    user_id = data.get('userId')
    assigned_to_user_id = data.get('assignedToUserId')  # NUEVO
    
    # Si es admin y especifica un tutor, usar ese tutor
    # Si no, usar el user_id actual
    added_by_user_id = assigned_to_user_id if assigned_to_user_id else user_id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO attendance_roster (employee_id, added_by_user_id)
            VALUES (%s, %s)
            ON CONFLICT (employee_id) DO NOTHING
        """, (employee_id, added_by_user_id))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Colaborador agregado'})
    finally:
        conn.close()
```

#### B. Endpoint: POST /api/incidents (Crear incidencia)
Ya existe, solo agregar soporte para `assignedToUserId`:
```python
# En la línea donde se obtiene reported_by, agregar:
assigned_to_user_id = data.get('assignedToUserId')
if assigned_to_user_id:
    # Admin está creando para un tutor
    reported_by = assigned_to_user_id
else:
    # Usuario normal o admin creando para sí mismo
    reported_by = data.get('reported_by') or data.get('employee_id') or None
```

#### C. Endpoint: POST /api/attendance/mark (Crear asistencia)
Similar al de incidencias, agregar soporte para asignación.

### 2. FRONTEND - Modificar Modales

#### A. Modal de Agregar Colaborador al Roster
Agregar después del campo de selección de empleado:

```html
<!-- Solo visible para admins -->
<div id="tutorAssignmentField" style="display: none; margin-top: 1rem;">
    <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">
        Asignar a tutor:
    </label>
    <select id="assignToTutor" style="width: 100%; padding: 0.6rem; border: 1px solid #cbd5e1; border-radius: 6px;">
        <option value="">Seleccionar tutor...</option>
        <!-- Se llenará dinámicamente -->
    </select>
</div>
```

JavaScript para cargar tutores:
```javascript
async function openRosterModal() {
    document.getElementById('rosterModal').style.display = 'flex';
    
    // Verificar si es admin
    const userStr = sessionStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;
    
    if (user && user.role === 'admin') {
        // Mostrar campo de asignación
        document.getElementById('tutorAssignmentField').style.display = 'block';
        
        // Cargar tutores supervisados
        try {
            const res = await fetch(`${API_BASE_URL}/supervised-tutors?userId=${user.id}`);
            const result = await res.json();
            
            if (result.success && result.tutors) {
                const select = document.getElementById('assignToTutor');
                select.innerHTML = '<option value="">Seleccionar tutor...</option>';
                
                result.tutors.forEach(tutor => {
                    const opt = document.createElement('option');
                    opt.value = tutor.id;
                    opt.textContent = tutor.username;
                    select.appendChild(opt);
                });
            }
        } catch (e) {
            console.error('Error loading tutors', e);
        }
    } else {
        document.getElementById('tutorAssignmentField').style.display = 'none';
    }
}
```

Modificar función de guardar:
```javascript
async function saveToRoster() {
    const employeeId = document.getElementById('rosterEmployee').value;
    const assignedToUserId = document.getElementById('assignToTutor').value;
    
    const userStr = sessionStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;
    
    const payload = {
        employee_id: employeeId,
        userId: user.id
    };
    
    // Si es admin y seleccionó un tutor, agregar assignedToUserId
    if (user.role === 'admin' && assignedToUserId) {
        payload.assignedToUserId = assignedToUserId;
    }
    
    try {
        const res = await fetch(`${API_BASE_URL}/attendance/roster`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const result = await res.json();
        if (result.success) {
            closeRosterModal();
            fetchAndRenderAttendance();
            showToast('Colaborador agregado', 'success');
        }
    } catch (e) {
        showToast('Error al agregar', 'error');
    }
}
```

#### B. Modal de Nueva Incidencia
Similar al modal de roster, agregar el mismo campo de asignación de tutor.

#### C. Modal de Nueva Asistencia
Similar implementación.

### 3. PERMISOS - Modificar Lógica de Visualización

Los admins ya pueden VER la información de sus tutores gracias a `get_authorized_user_ids()`.
No se necesitan cambios adicionales para visualización.

### 4. PERMISOS - Permitir Edición/Eliminación

Los admins ya pueden editar/eliminar porque los endpoints no tienen restricciones adicionales.
La información sigue perteneciendo al tutor que la creó originalmente.

## Resumen de Archivos a Modificar

1. **app.py**:
   - ✅ Agregar endpoint `/api/supervised-tutors` (HECHO)
   - ⏳ Modificar POST `/api/attendance/roster` para aceptar `assignedToUserId`
   - ⏳ Modificar POST `/api/incidents` para aceptar `assignedToUserId`
   - ⏳ Modificar POST `/api/attendance/mark` para aceptar `assignedToUserId`

2. **dashboard.html**:
   - ⏳ Agregar campo de asignación de tutor en modal de roster
   - ⏳ Agregar campo de asignación de tutor en modal de incidencias
   - ⏳ Agregar campo de asignación de tutor en modal de asistencias
   - ⏳ Modificar funciones de guardar para enviar `assignedToUserId`

## Notas Importantes

- El campo de asignación solo se muestra si `user.role === 'admin'`
- Si el admin no selecciona un tutor, la información se asigna al admin mismo
- Los tutores nunca ven este campo (solo crean para sí mismos)
- La jerarquía se mantiene: admin solo ve sus 6 tutores supervisados
