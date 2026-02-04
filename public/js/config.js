// CONFIGURACIÓN DE CONEXIÓN AL SERVIDOR
// Detecta automáticamente si está en local o en Railway

const API_BASE_URL = window.location.origin + '/api';

console.log('API Base URL:', API_BASE_URL);

// Global Holidays Cache
let holidaysCache = {};

async function fetchHolidays(year) {
    if (holidaysCache[year]) return holidaysCache[year];
    try {
        const res = await fetch(`${API_BASE_URL}/holidays/${year}`);
        const result = await res.json();
        if (result.success) {
            holidaysCache[year] = result.data;
            return result.data;
        }
    } catch (e) { console.error('Error fetching holidays', e); }
    return [];
}
