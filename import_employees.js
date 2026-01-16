const XLSX = require('xlsx');
const path = require('path');
const db = require('./database');

const filePath = path.join(__dirname, 'Plantilla Asisitentes de sucursal 31-12-2025.xlsx');

function excelDateToJSDate(serial) {
    if (!serial) return null;
    return new Date(Math.round((serial - 25569) * 86400 * 1000));
}

function formatDate(dateObj) {
    if (!dateObj) return null;
    return dateObj.toISOString().split('T')[0]; // YYYY-MM-DD
}

function runImport() {
    console.log('--- INICIANDO IMPORTACIÓN ---');

    const workbook = XLSX.readFile(filePath);
    const sheet = workbook.Sheets[workbook.SheetNames[0]];
    const rows = XLSX.utils.sheet_to_json(sheet); // Obj key-value based on headers

    console.log(`Leídos ${rows.length} empleados del Excel.`);

    db.serialize(() => {
        // 1. Extract Unique Branches
        const uniqueBranches = new Set();
        rows.forEach(row => {
            const branchName = row[' SUCURSAL'];
            if (branchName) uniqueBranches.add(branchName.trim());
        });

        console.log(`Encontradas ${uniqueBranches.size} sucursales únicas.`);

        // 2. Insert Branches
        const insertBranch = db.prepare('INSERT OR IGNORE INTO branches (name) VALUES (?)');
        uniqueBranches.forEach(branch => {
            insertBranch.run(branch);
        });
        insertBranch.finalize();

        // 3. Load Branch Map (Name -> ID)
        db.all('SELECT id, name FROM branches', (err, branchesDB) => {
            if (err) {
                console.error('Error loading branches:', err);
                return;
            }

            const branchMap = {};
            branchesDB.forEach(b => branchMap[b.name] = b.id);

            // 4. Insert Employees
            const insertEmp = db.prepare(`
                INSERT INTO employees (full_name, branch_id, hire_date, status) 
                VALUES (?, ?, ?, 'active')
            `);

            let count = 0;
            db.serialize(() => {
                db.run("BEGIN TRANSACTION");

                rows.forEach(row => {
                    const name = row[' NOMBRE'];
                    const branchName = row[' SUCURSAL'] ? row[' SUCURSAL'].trim() : null;
                    const dateSerial = row[' FECHA DE INGRESO'];

                    if (name && branchName) {
                        const branchId = branchMap[branchName];
                        const hireDate = formatDate(excelDateToJSDate(dateSerial));

                        insertEmp.run(name, branchId, hireDate, (err) => {
                            if (err) console.error('Error insertando:', name, err.message);
                        });
                        count++;
                    }
                });

                db.run("COMMIT", () => {
                    console.log(`✅ Importación finalizada. ${count} empleados insertados.`);
                    insertEmp.finalize();
                });
            });
        });
    });
}

runImport();
