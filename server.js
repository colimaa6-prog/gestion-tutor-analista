require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');
const db = require('./database');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// Authorization Helper Function
function getAuthorizedUserIds(userId, callback) {
    // First get the user to check their role
    db.get('SELECT id, role, supervisor_id FROM users WHERE id = ?', [userId], (err, user) => {
        if (err || !user) {
            return callback(err, []);
        }

        if (user.role === 'admin') {
            // Admin can see all users they supervise
            db.all('SELECT id FROM users WHERE supervisor_id = ?', [userId], (err, rows) => {
                if (err) return callback(err, []);
                const userIds = rows.map(r => r.id);
                callback(null, userIds);
            });
        } else {
            // Regular user can only see themselves
            callback(null, [userId]);
        }
    });
}

// Routes
app.get('/api/health', (req, res) => {
    res.json({ status: 'OK', message: 'Server is running' });
});

// Login Endpoint
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ success: false, message: 'Usuario y contraseña requeridos' });
    }

    const query = 'SELECT * FROM users WHERE username = ?';
    db.get(query, [username], (err, user) => {
        if (err) {
            console.error('Error querying database:', err);
            return res.status(500).json({ success: false, message: 'Error del servidor' });
        }

        if (!user) {
            return res.status(401).json({ success: false, message: 'Usuario no encontrado' });
        }

        // In a real production app, use bcrypt.compare here. 
        // For MVP with seed data, we compare directly.
        if (user.password_hash !== password) {
            return res.status(401).json({ success: false, message: 'Contraseña incorrecta' });
        }

        // Get supervised users if admin
        getAuthorizedUserIds(user.id, (err, supervisedUserIds) => {
            if (err) {
                console.error('Error getting supervised users:', err);
                return res.status(500).json({ success: false, message: 'Error del servidor' });
            }

            // Login successful
            res.json({
                success: true,
                message: 'Bienvenido',
                user: {
                    id: user.id,
                    username: user.username,
                    role: user.role,
                    branch_id: user.branch_id,
                    supervisor_id: user.supervisor_id,
                    supervised_user_ids: supervisedUserIds
                }
            });
        });
    });
});


// Get Employees Endpoint
app.get('/api/employees', (req, res) => {
    const query = `
        SELECT e.id, e.full_name, e.branch_id, e.hire_date, e.status, b.name as branch_name 
        FROM employees e 
        LEFT JOIN branches b ON e.branch_id = b.id
        ORDER BY e.full_name ASC
    `;
    db.all(query, [], (err, rows) => {
        if (err) {
            console.error('Error fetching employees:', err);
            return res.status(500).json({ success: false, message: 'Error al obtener empleados' });
        }
        res.json({ success: true, data: rows });
    });
});

// Get Branches Endpoint (for dropdowns)
app.get('/api/branches', (req, res) => {
    db.all('SELECT * FROM branches ORDER BY name ASC', [], (err, rows) => {
        if (err) return res.status(500).json({ success: false, message: 'Error' });
        res.json({ success: true, data: rows });
    });
});

// Create Employee Endpoint
app.post('/api/employees', (req, res) => {
    const { full_name, branch_id, hire_date } = req.body;
    if (!full_name || !branch_id) {
        return res.status(400).json({ success: false, message: 'Nombre y Sucursal son obligatorios' });
    }

    const query = 'INSERT INTO employees (full_name, branch_id, hire_date, status) VALUES (?, ?, ?, "active")';
    db.run(query, [full_name, branch_id, hire_date], function (err) {
        if (err) {
            console.error(err);
            return res.status(500).json({ success: false, message: 'Error al agregar' });
        }
        // Oracle adapter doesn't return lastID automatically. Fetch it.
        db.get('SELECT id FROM employees WHERE full_name = ? AND branch_id = ? ORDER BY id DESC', [full_name, branch_id], (err, row) => {
            res.json({ success: true, message: 'Agregado correctamente', id: row ? row.id : 0 });
        });
    });
});

// Update Employee Endpoint
app.put('/api/employees/:id', (req, res) => {
    const { full_name, branch_id, hire_date } = req.body;
    const id = req.params.id;

    if (!full_name || !branch_id) {
        return res.status(400).json({ success: false, message: 'Nombre y Sucursal son obligatorios' });
    }

    const query = 'UPDATE employees SET full_name = ?, branch_id = ?, hire_date = ? WHERE id = ?';
    db.run(query, [full_name, branch_id, hire_date, id], function (err) {
        if (err) {
            console.error(err);
            return res.status(500).json({ success: false, message: 'Error al actualizar' });
        }
        res.json({ success: true, message: 'Actualizado correctamente' });
    });
});

// Delete Employee Endpoint
app.delete('/api/employees/:id', (req, res) => {
    const id = req.params.id;
    db.run('DELETE FROM employees WHERE id = ?', [id], function (err) {
        if (err) {
            console.error(err);
            return res.status(500).json({ success: false, message: 'Error al eliminar' });
        }
        res.json({ success: true, message: 'Eliminado correctamente' });
    });
});

// --- ATTENDANCE APIS ---

// Get Roster + Attendance Data for a specific month
app.get('/api/attendance', (req, res) => {
    const { month, year, userId } = req.query; // e.g. month=0 (Jan), year=2024

    if (!userId) {
        return res.status(400).json({ success: false, message: 'userId is required' });
    }

    // Get authorized user IDs first
    getAuthorizedUserIds(parseInt(userId), (err, authorizedUserIds) => {
        if (err || authorizedUserIds.length === 0) {
            return res.json({ success: true, data: [] });
        }

        // Build placeholders for SQL IN clause
        const placeholders = authorizedUserIds.map(() => '?').join(',');

        // 1. Get Roster Employees (filtered by who added them)
        // Tutors see only employees they added
        // Admins see employees added by their supervised tutors
        const qRoster = `
            SELECT e.id, e.full_name, e.branch_id, b.name as branch_name 
            FROM attendance_roster ar
            JOIN employees e ON ar.employee_id = e.id
            LEFT JOIN branches b ON e.branch_id = b.id
            WHERE ar.added_by_user_id IN (${placeholders})
            ORDER BY e.full_name ASC
        `;

        db.all(qRoster, authorizedUserIds, (err, employees) => {
            if (err) return res.status(500).json({ success: false, message: 'Error fetching roster' });

            if (employees.length === 0) {
                return res.json({ success: true, data: [] });
            }

            // 2. Get Attendance Marks for these employees in the given month
            // Construct date range string 'YYYY-MM-%'
            // Note: Javascript months are 0-11, DB stores YYYY-MM-DD
            const m = parseInt(month) + 1;
            const monthStr = m < 10 ? `0${m}` : `${m}`;
            const datePattern = `${year}-${monthStr}-%`;

            const qAtt = `SELECT * FROM attendance WHERE date LIKE ?`;
            db.all(qAtt, [datePattern], (err, marks) => {
                if (err) return res.status(500).json({ success: false, message: 'Error fetching marks' });

                // Combine data
                const rosterWithMarks = employees.map(emp => {
                    const empMarks = marks.filter(mk => mk.employee_id === emp.id);
                    // Convert to map with full attendance data: { '2024-01-01': { status: 'present', comment: '...', ... }, ... }
                    const marksMap = {};
                    empMarks.forEach(mk => {
                        marksMap[mk.date] = {
                            status: mk.status,
                            comment: mk.comment,
                            arrival_time: mk.arrival_time,
                            permission_type: mk.permission_type,
                            start_date: mk.start_date,
                            end_date: mk.end_date
                        };
                    });
                    return { ...emp, marks: marksMap };
                });

                res.json({ success: true, data: rosterWithMarks });
            });
        });
    });
});

// Add Employee to Roster
app.post('/api/attendance/roster', (req, res) => {
    const { employee_id, userId } = req.body;
    db.run('INSERT OR REPLACE INTO attendance_roster (employee_id, added_by_user_id) VALUES (?, ?)', [employee_id, userId], (err) => {
        if (err) return res.status(500).json({ success: false, message: 'Error adding to roster' });
        res.json({ success: true });
    });
});

// Remove from Roster (Optional, maybe for cleanup)
app.delete('/api/attendance/roster/:id', (req, res) => {
    db.run('DELETE FROM attendance_roster WHERE employee_id = ?', [req.params.id], (err) => {
        if (err) return res.status(500).json({ success: false, message: 'Error removing' });
        res.json({ success: true });
    });
});

// Get Archived Months (months with attendance data)
app.get('/api/attendance/archived-months', (req, res) => {
    const query = `
        SELECT DISTINCT 
            CAST(strftime('%m', date) AS INTEGER) - 1 as month,
            CAST(strftime('%Y', date) AS INTEGER) as year,
            COUNT(*) as record_count
        FROM attendance
        GROUP BY strftime('%Y-%m', date)
        ORDER BY year DESC, month DESC
    `;

    db.all(query, [], (err, rows) => {
        if (err) {
            console.error('Error fetching archived months:', err);
            return res.status(500).json({ success: false, message: 'Error fetching archived months' });
        }
        res.json({ success: true, data: rows });
    });
});

// Mark Attendance
app.post('/api/attendance/mark', (req, res) => {
    const { employee_id, date, status, comment, arrival_time, permission_type, start_date, end_date } = req.body;

    // Check if exists
    db.get('SELECT id FROM attendance WHERE employee_id = ? AND date = ?', [employee_id, date], (err, row) => {
        if (err) return res.status(500).json({ success: false, message: 'Error checking DB' });

        if (row) {
            // Update
            if (status === 'none') {
                // Remove if status is cleared
                db.run('DELETE FROM attendance WHERE id = ?', [row.id], (err) => {
                    if (err) return res.status(500).json({ success: false, message: 'Error deleting' });
                    res.json({ success: true });
                });
            } else {
                const updateQuery = `UPDATE attendance SET 
                    status = ?, 
                    comment = ?, 
                    arrival_time = ?, 
                    permission_type = ?, 
                    start_date = ?, 
                    end_date = ? 
                    WHERE id = ?`;
                db.run(updateQuery, [status, comment || null, arrival_time || null, permission_type || null, start_date || null, end_date || null, row.id], (err) => {
                    if (err) return res.status(500).json({ success: false, message: 'Error updating' });
                    res.json({ success: true });
                });
            }
        } else {
            // Insert
            if (status !== 'none') {
                const insertQuery = `INSERT INTO attendance 
                    (employee_id, date, status, comment, arrival_time, permission_type, start_date, end_date) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)`;
                db.run(insertQuery, [employee_id, date, status, comment || null, arrival_time || null, permission_type || null, start_date || null, end_date || null], (err) => {
                    if (err) return res.status(500).json({ success: false, message: 'Error inserting' });
                    res.json({ success: true });
                });
            } else {
                res.json({ success: true }); // Nothing to do
            }
        }
    });
});


// --- INCIDENTS APIS ---

// Get Incidents
app.get('/api/incidents', (req, res) => {
    const query = `
        SELECT i.*, e.full_name as reported_by_name, b.name as branch_name 
        FROM incidents i
        JOIN employees e ON i.reported_by = e.id
        LEFT JOIN branches b ON i.branch_id = b.id
        ORDER BY i.created_at DESC
    `;
    db.all(query, [], (err, rows) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ success: false, message: 'Error fetching incidents' });
        }
        res.json({ success: true, data: rows });
    });
});

// Create Incident
app.post('/api/incidents', (req, res) => {
    const { employee_id, type, status, start_date, end_date, description } = req.body;

    // First get branch_id from employee
    db.get('SELECT branch_id FROM employees WHERE id = ?', [employee_id], (err, emp) => {
        if (err || !emp) {
            return res.status(400).json({ success: false, message: 'Empleado no válido' });
        }

        const query = `INSERT INTO incidents 
            (branch_id, reported_by, type, status, description, start_date, end_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?)`;

        const safeEndDate = end_date === '' ? null : end_date;
        const safeStartDate = start_date === '' ? null : start_date;

        db.run(query, [emp.branch_id, employee_id, type, status, description, safeStartDate, safeEndDate], function (err) {
            if (err) {
                console.error('INSERT ERROR:', err);
                return res.status(500).json({ success: false, message: 'Error creando incidencia: ' + err.message });
            }
            // Fetch ID
            db.get('SELECT id FROM incidents WHERE reported_by = ? ORDER BY id DESC', [employee_id], (err, row) => {
                res.json({ success: true, message: 'Reporte creado', id: row ? row.id : 0 });
            });
        });
    });
});

// Update Incident
app.put('/api/incidents/:id', (req, res) => {
    const { employee_id, type, status, start_date, end_date, description } = req.body;
    const id = req.params.id;

    // We allow updating employee_id, so we need to get the branch again just in case
    db.get('SELECT branch_id FROM employees WHERE id = ?', [employee_id], (err, emp) => {
        if (err || !emp) {
            return res.status(400).json({ success: false, message: 'Empleado no válido' });
        }

        const query = `UPDATE incidents SET 
            branch_id = ?, 
            reported_by = ?, 
            type = ?, 
            status = ?, 
            description = ?, 
            start_date = ?, 
            end_date = ? 
            WHERE id = ?`;

        const safeEndDate = end_date === '' ? null : end_date;
        const safeStartDate = start_date === '' ? null : start_date;

        db.run(query, [emp.branch_id, employee_id, type, status, description, safeStartDate, safeEndDate, id], function (err) {
            if (err) {
                console.error('UPDATE ERROR:', err);
                return res.status(500).json({ success: false, message: 'Error actualizando: ' + err.message });
            }
            res.json({ success: true, message: 'Actualizado correctamente' });
        });
    });
});

// Delete Incident
app.delete('/api/incidents/:id', (req, res) => {
    db.run('DELETE FROM incidents WHERE id = ?', [req.params.id], (err) => {
        if (err) return res.status(500).json({ success: false, message: 'Error al eliminar' });
        res.json({ success: true, message: 'Eliminado correctamente' });
    });
});


// --- REPORTS APIS ---

// Get Monthly Reports (joined with Roster)
app.get('/api/reports', (req, res) => {
    const { month, year, userId } = req.query;

    if (!userId) {
        return res.status(400).json({ success: false, message: 'userId is required' });
    }

    // Get authorized user IDs first
    getAuthorizedUserIds(parseInt(userId), (err, authorizedUserIds) => {
        if (err || authorizedUserIds.length === 0) {
            return res.json({ success: true, data: [] });
        }

        // Build placeholders for SQL IN clause
        const placeholders = authorizedUserIds.map(() => '?').join(',');

        // Get roster employees (filtered by who added them)
        // Tutors see only employees they added
        // Admins see employees added by their supervised tutors
        const qRoster = `
            SELECT e.id, e.full_name, e.branch_id, b.name as branch_name 
            FROM attendance_roster ar
            JOIN employees e ON ar.employee_id = e.id
            LEFT JOIN branches b ON e.branch_id = b.id
            WHERE ar.added_by_user_id IN (${placeholders})
            ORDER BY e.full_name ASC
        `;

        db.all(qRoster, authorizedUserIds, (err, employees) => {
            if (err) return res.status(500).json({ success: false, message: 'Error fetching roster' });

            if (employees.length === 0) return res.json({ success: true, data: [] });

            // Get reports for this month/year
            db.all('SELECT * FROM reports WHERE month = ? AND year = ?', [month, year], (err, reports) => {
                if (err) return res.status(500).json({ success: false, message: 'Error fetching reports' });

                // Combine
                const combined = employees.map(emp => {
                    const rep = reports.find(r => r.employee_id === emp.id);
                    return {
                        ...emp,
                        report_data: rep ? rep.data : null
                    };
                });

                res.json({ success: true, data: combined });
            });
        });
    });
});

// Get Archived Months for Reports
app.get('/api/reports/archived-months', (req, res) => {
    const query = `
        SELECT DISTINCT 
            month,
            year,
            COUNT(*) as record_count
        FROM reports
        GROUP BY year, month
        ORDER BY year DESC, month DESC
    `;

    db.all(query, [], (err, rows) => {
        if (err) {
            console.error('Error fetching archived months for reports:', err);
            return res.status(500).json({ success: false, message: 'Error fetching archived months' });
        }
        res.json({ success: true, data: rows });
    });
});

// Update Report Cell
app.post('/api/reports', (req, res) => {
    const { employee_id, month, year, type, key, status, comment } = req.body;
    // type: 'faltantes', 'guias', 'tableros'
    // key: day number (1-31) or week num (1-4) or quincena (1-2)

    db.get('SELECT id, data FROM reports WHERE employee_id = ? AND month = ? AND year = ?', [employee_id, month, year], (err, row) => {
        if (err) return res.status(500).json({ success: false, message: 'DB Error' });

        let data = { faltantes: {}, guias: {}, tableros: {} };
        if (row && row.data) {
            try { data = JSON.parse(row.data); } catch (e) { }
        }

        // Update specific key
        if (!data[type]) data[type] = {};

        if (status === 'empty') {
            delete data[type][key];
        } else {
            data[type][key] = { status, comment };
        }

        const jsonStr = JSON.stringify(data);

        if (row) {
            // Update
            db.run('UPDATE reports SET data = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', [jsonStr, row.id], (err) => {
                if (err) return res.status(500).json({ success: false, message: 'Update failed' });
                res.json({ success: true });
            });
        } else {
            // Insert
            db.run('INSERT INTO reports (employee_id, month, year, data) VALUES (?, ?, ?, ?)', [employee_id, month, year, jsonStr], (err) => {
                if (err) return res.status(500).json({ success: false, message: 'Insert failed' });
                res.json({ success: true });
            });
        }
    });
});


// --- DASHBOARD APIS ---

// Get Dashboard Statistics
app.get('/api/dashboard/stats', (req, res) => {
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const { userId } = req.query;

    if (!userId) {
        return res.status(400).json({ success: false, message: 'userId is required' });
    }

    // Get authorized user IDs first
    getAuthorizedUserIds(parseInt(userId), (err, authorizedUserIds) => {
        if (err || authorizedUserIds.length === 0) {
            return res.json({ success: true, data: { asistencias: 0, faltas: 0, vacaciones: 0, permisos: 0, incapacidades: 0, incidencias_activas: 0 } });
        }

        // Build placeholders for SQL IN clause
        const placeholders = authorizedUserIds.map(() => '?').join(',');

        // Get today's attendance counts (filtered by authorized users)
        const attendanceQuery = `
            SELECT status, COUNT(*) as count 
            FROM attendance 
            WHERE date = ? AND employee_id IN (${placeholders})
            GROUP BY status
        `;

        db.all(attendanceQuery, [today, ...authorizedUserIds], (err, attendanceRows) => {
            if (err) return res.status(500).json({ success: false, message: 'Error fetching attendance' });

            // Get active incidents count (filtered by authorized users)
            const incidentQuery = `
                SELECT COUNT(*) as count 
                FROM incidents 
                WHERE status IN ('pending', 'in_progress') 
                AND reported_by IN (${placeholders})
            `;

            db.get(incidentQuery, authorizedUserIds, (err, incidentRow) => {
                if (err) return res.status(500).json({ success: false, message: 'Error fetching incidents' });

                // Process attendance data
                const stats = {
                    asistencias: 0,
                    faltas: 0,
                    vacaciones: 0,
                    permisos: 0,
                    incapacidades: 0,
                    incidencias_activas: incidentRow.count
                };

                attendanceRows.forEach(row => {
                    if (row.status === 'present') stats.asistencias = row.count;
                    else if (row.status === 'absent') stats.faltas = row.count;
                    else if (row.status === 'vacation') stats.vacaciones = row.count;
                    else if (row.status === 'permission') stats.permisos = row.count;
                    else if (row.status === 'incapacity') stats.incapacidades = row.count;
                });

                res.json({ success: true, data: stats });
            });
        });
    });
});

// Get Today's Absences
app.get('/api/dashboard/absences', (req, res) => {
    const today = new Date().toISOString().split('T')[0];
    const { userId } = req.query;

    if (!userId) {
        return res.status(400).json({ success: false, message: 'userId is required' });
    }

    getAuthorizedUserIds(parseInt(userId), (err, authorizedUserIds) => {
        if (err || authorizedUserIds.length === 0) {
            return res.json({ success: true, data: [] });
        }

        const placeholders = authorizedUserIds.map(() => '?').join(',');
        const query = `
            SELECT e.id, e.full_name, b.name as branch_name, a.comment
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            LEFT JOIN branches b ON e.branch_id = b.id
            WHERE a.date = ? AND a.status = 'absent' AND a.employee_id IN (${placeholders})
            ORDER BY e.full_name ASC
        `;

        db.all(query, [today, ...authorizedUserIds], (err, rows) => {
            if (err) return res.status(500).json({ success: false, message: 'Error' });
            res.json({ success: true, data: rows });
        });
    });
});

// Get Active Vacations
app.get('/api/dashboard/vacations', (req, res) => {
    const today = new Date().toISOString().split('T')[0];
    const { userId } = req.query;

    if (!userId) {
        return res.status(400).json({ success: false, message: 'userId is required' });
    }

    getAuthorizedUserIds(parseInt(userId), (err, authorizedUserIds) => {
        if (err || authorizedUserIds.length === 0) {
            return res.json({ success: true, data: [] });
        }

        const placeholders = authorizedUserIds.map(() => '?').join(',');
        const query = `
            SELECT e.id, e.full_name, b.name as branch_name, a.start_date, a.end_date, a.comment
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            LEFT JOIN branches b ON e.branch_id = b.id
            WHERE a.status = 'vacation' 
            AND a.start_date <= ? 
            AND a.end_date >= ?
            AND a.employee_id IN (${placeholders})
            ORDER BY e.full_name ASC
        `;

        db.all(query, [today, today, ...authorizedUserIds], (err, rows) => {
            if (err) return res.status(500).json({ success: false, message: 'Error' });
            res.json({ success: true, data: rows });
        });
    });
});

// Get Active Permissions
app.get('/api/dashboard/permissions', (req, res) => {
    const today = new Date().toISOString().split('T')[0];
    const { userId } = req.query;

    if (!userId) {
        return res.status(400).json({ success: false, message: 'userId is required' });
    }

    getAuthorizedUserIds(parseInt(userId), (err, authorizedUserIds) => {
        if (err || authorizedUserIds.length === 0) {
            return res.json({ success: true, data: [] });
        }

        const placeholders = authorizedUserIds.map(() => '?').join(',');
        const query = `
            SELECT e.id, e.full_name, b.name as branch_name, a.permission_type, a.start_date, a.end_date, a.comment
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            LEFT JOIN branches b ON e.branch_id = b.id
            WHERE a.status = 'permission' 
            AND a.start_date <= ? 
            AND a.end_date >= ?
            AND a.employee_id IN (${placeholders})
            ORDER BY e.full_name ASC
        `;

        db.all(query, [today, today, ...authorizedUserIds], (err, rows) => {
            if (err) return res.status(500).json({ success: false, message: 'Error' });
            res.json({ success: true, data: rows });
        });
    });
});

// Get Active Sick Leaves
app.get('/api/dashboard/sick-leaves', (req, res) => {
    const today = new Date().toISOString().split('T')[0];
    const { userId } = req.query;

    if (!userId) {
        return res.status(400).json({ success: false, message: 'userId is required' });
    }

    getAuthorizedUserIds(parseInt(userId), (err, authorizedUserIds) => {
        if (err || authorizedUserIds.length === 0) {
            return res.json({ success: true, data: [] });
        }

        const placeholders = authorizedUserIds.map(() => '?').join(',');
        const query = `
            SELECT e.id, e.full_name, b.name as branch_name, a.start_date, a.end_date, a.comment
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            LEFT JOIN branches b ON e.branch_id = b.id
            WHERE a.status = 'incapacity' 
            AND a.start_date <= ? 
            AND a.end_date >= ?
            AND a.employee_id IN (${placeholders})
            ORDER BY e.full_name ASC
        `;

        db.all(query, [today, today, ...authorizedUserIds], (err, rows) => {
            if (err) return res.status(500).json({ success: false, message: 'Error' });
            res.json({ success: true, data: rows });
        });
    });
});

// Get Active Incidents
app.get('/api/dashboard/active-incidents', (req, res) => {
    const { userId } = req.query;

    if (!userId) {
        return res.status(400).json({ success: false, message: 'userId is required' });
    }

    getAuthorizedUserIds(parseInt(userId), (err, authorizedUserIds) => {
        if (err || authorizedUserIds.length === 0) {
            return res.json({ success: true, data: [] });
        }

        const placeholders = authorizedUserIds.map(() => '?').join(',');
        const query = `
            SELECT i.*, e.full_name as reported_by_name, b.name as branch_name
            FROM incidents i
            JOIN employees e ON i.reported_by = e.id
            LEFT JOIN branches b ON i.branch_id = b.id
            WHERE i.status IN ('pending', 'in_progress')
            AND i.reported_by IN (${placeholders})
            ORDER BY i.created_at DESC
        `;

        db.all(query, authorizedUserIds, (err, rows) => {
            if (err) return res.status(500).json({ success: false, message: 'Error' });
            res.json({ success: true, data: rows });
        });
    });
});


// Serve frontend
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, '127.0.0.1', () => {
    console.log(`Server running on http://127.0.0.1:${PORT}`);
    console.log('Press Ctrl+C to stop');
});



