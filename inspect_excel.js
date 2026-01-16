const XLSX = require('xlsx');
const path = require('path');

const filePath = path.join(__dirname, 'Plantilla Asisitentes de sucursal 31-12-2025.xlsx');
console.log('Leyendo archivo:', filePath);

try {
    const workbook = XLSX.readFile(filePath);
    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];

    // Convert to JSON to see headers and first row
    const data = XLSX.utils.sheet_to_json(sheet, { header: 1 });

    console.log('--- ENCABEZADOS (Fila 1) ---');
    console.log(data[0]);

    console.log('--- PRIMER EMPLEADO (Fila 2) ---');
    console.log(data[1]);

} catch (error) {
    console.error('Error al leer el archivo:', error.message);
}
