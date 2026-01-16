// Reports Module Logic

async function loadReportes() {
    updateActiveLink('Reportes');
    document.getElementById('pageTitle').innerText = 'Reportes de Gestión';
    document.getElementById('statsGrid').style.display = 'none'; // Hide stats for now

    const content = document.getElementById('contentArea');

    // Fetch archived months
    let archivedMonthsHTML = '';
    try {
        const res = await fetch(`${API_BASE_URL}/reports/archived-months`);
        const result = await res.json();

        if (result.success && result.data.length > 0) {
            const today = new Date();
            const currentMonthKey = `${today.getFullYear()}-${today.getMonth()}`;

            // Filter out current month from archives
            const archivedMonths = result.data.filter(m => `${m.year}-${m.month}` !== currentMonthKey);

            if (archivedMonths.length > 0) {
                archivedMonthsHTML = `
                    <div style="margin-bottom: 2rem;">
                        <h4 style="margin: 0 0 1rem 0; color: #64748b; font-size: 0.9rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Meses Archivados</h4>
                        <div style="display: flex; gap: 1rem; overflow-x: auto; padding-bottom: 0.5rem;">
                            ${archivedMonths.map(m => `
                                <div onclick="loadReportsMonthData(${m.month}, ${m.year})" 
                                     style="min-width: 140px; padding: 1rem 1.25rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                            border-radius: 12px; cursor: pointer; transition: all 0.3s ease; 
                                            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"
                                     onmouseover="this.style.transform='translateY(-2px) scale(1.02)'; this.style.boxShadow='0 10px 15px -3px rgba(0, 0, 0, 0.2)';"
                                     onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 4px 6px -1px rgba(0, 0, 0, 0.1)';">
                                    <div style="color: white; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.25rem;">${monthNames[m.month]}</div>
                                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 0.85rem; margin-bottom: 0.5rem;">${m.year}</div>
                                    <div style="color: rgba(255, 255, 255, 0.8); font-size: 0.75rem; display: flex; align-items: center; gap: 0.25rem;">
                                        📁 ${m.record_count} registros
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
        }
    } catch (e) {
        console.error('Error loading archived months:', e);
    }

    // Check if viewing current month
    const today = new Date();
    const isCurrentMonth = (currentYear === today.getFullYear() && currentMonth === today.getMonth());

    const monthHeaderStyle = isCurrentMonth
        ? 'background: white; color: #1e293b; border: 2px solid #e2e8f0;'
        : 'background: white; color: #1e293b; border: 2px solid #e2e8f0;';

    const monthBadge = isCurrentMonth
        ? '<span style="background: #f1f5f9; color: #64748b; padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 600;">MES ACTUAL</span>'
        : '<button onclick="loadCurrentReportsMonth()" style="background: #f8fafc; border: 1px solid #cbd5e1; color: #475569; padding: 0.4rem 0.8rem; border-radius: 8px; font-size: 0.8rem; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background=\'#e2e8f0\'" onmouseout="this.style.background=\'#f8fafc\'">← Volver al Mes Actual</button>';

    content.innerHTML = `
        ${archivedMonthsHTML}
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding: 1.25rem; border-radius: 12px; ${monthHeaderStyle} box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <h3 style="margin: 0; font-size: 1.5rem; color: #1e293b;">${monthNames[currentMonth]} ${currentYear}</h3>
                ${monthBadge}
            </div>
            <div style="font-size: 0.9rem; color: #64748b;">
                <span style="margin-right: 1rem;">ℹ️ Click para seleccionar: ✅ Palomita o ❌ Equis</span>
            </div>
        </div>

        <div style="overflow-x: auto; padding-bottom: 2rem;">
            <table style="width: 100%; border-collapse: separate; border-spacing: 0;">
                <tbody id="reportsBody">
                    <tr><td style="padding: 2rem; text-align: center;">Cargando reportes...</td></tr>
                </tbody>
            </table>
        </div>

        <!-- Selection Modal for Icon Choice -->
        <div id="reportSelectionModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); justify-content: center; align-items: center; z-index: 10000;">
            <div style="background: white; padding: 2rem; border-radius: 12px; width: 400px; max-width: 90%;">
                <h3 style="margin-top: 0;">Seleccionar Estado</h3>
                <p style="font-size: 0.9rem; color: #64748b; margin-bottom: 1rem;">Elige el estado para este registro:</p>
                <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
                    <button onclick="selectReportStatus('check')" style="flex: 1; padding: 1.5rem; background: #f0fdf4; border: 2px solid #22c55e; border-radius: 8px; cursor: pointer; font-size: 2rem; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        ✅
                        <div style="font-size: 0.85rem; color: #166534; margin-top: 0.5rem;">Palomita</div>
                    </button>
                    <button onclick="selectReportStatus('cross')" style="flex: 1; padding: 1.5rem; background: #fef2f2; border: 2px solid #ef4444; border-radius: 8px; cursor: pointer; font-size: 2rem; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        ❌
                        <div style="font-size: 0.85rem; color: #991b1b; margin-top: 0.5rem;">Equis</div>
                    </button>
                </div>
                <div style="display: flex; justify-content: space-between; gap: 0.5rem;">
                    <button onclick="selectReportStatus('empty')" style="flex: 1; padding: 0.6rem 1rem; background: transparent; border: 1px solid #cbd5e1; border-radius: 6px; cursor: pointer;">Limpiar</button>
                    <button onclick="closeReportSelection()" style="flex: 1; padding: 0.6rem 1rem; background: transparent; border: 1px solid #cbd5e1; border-radius: 6px; cursor: pointer;">Cancelar</button>
                </div>
            </div>
        </div>

        <!-- Comment Modal for "Equis" (Cross) -->
        <div id="reportCommentModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); justify-content: center; align-items: center; z-index: 10001;">
            <div style="background: white; padding: 2rem; border-radius: 12px; width: 400px; max-width: 90%;">
                <h3 style="margin-top: 0;">Agregar Comentario</h3>
                <p style="font-size: 0.9rem; color: #64748b; margin-bottom: 1rem;">Justifica la falta de cumplimiento:</p>
                <textarea id="reportCommentInput" rows="4" style="width: 100%; padding: 0.8rem; border: 1px solid #cbd5e1; border-radius: 8px; font-family: inherit; margin-bottom: 1rem;"></textarea>
                <div style="display: flex; justify-content: flex-end; gap: 0.5rem;">
                    <button onclick="closeReportComment(false)" style="padding: 0.6rem 1rem; background: transparent; border: 1px solid #cbd5e1; border-radius: 6px; cursor: pointer;">Cancelar</button>
                    <button onclick="closeReportComment(true)" class="btn-primary" style="padding: 0.6rem 1rem;">Guardar</button>
                </div>
            </div>
        </div>
    `;

    await fetchAndRenderReports();
}

async function fetchAndRenderReports() {
    try {
        const userStr = sessionStorage.getItem('user');
        const user = userStr ? JSON.parse(userStr) : null;
        const userId = user ? user.id : null;

        const res = await fetch(`${API_BASE_URL}/reports?month=${currentMonth}&year=${currentYear}&userId=${userId}`);
        const result = await res.json();

        if (!result.success || !result.data || result.data.length === 0) {
            document.getElementById('reportsBody').innerHTML = '<tr><td style="padding: 2rem; text-align: center;">No hay colaboradores en la lista. Agrega colaboradores en la sección de Asistencias primero.</td></tr>';
            return;
        }

        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
        let html = '';

        result.data.forEach(emp => {
            // Parse existing data
            const reportData = emp.report_data ? JSON.parse(emp.report_data) : { faltantes: {}, guias: {}, tableros: {} };

            // --- ROW 1: Employee Header ---
            html += `
                <tr style="background: #f8fafc;">
                    <td colspan="33" style="padding: 1rem; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #1e293b;">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div style="width: 32px; height: 32px; background: #4f46e5; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.9rem;">
                                ${emp.full_name.charAt(0)}
                            </div>
                            ${emp.full_name}
                            <span style="font-size: 0.8rem; color: #64748b; font-weight: 400; margin-left: 0.5rem;">${emp.branch_name || ''}</span>
                        </div>
                    </td>
                </tr>
            `;

            // --- ROW 2: Reporte de Faltantes (Daily) ---
            html += `
                <tr>
                    <td style="padding: 0.3rem; background: #f1f5f9; font-size: 0.85rem; font-weight: 500; min-width: 150px; border-bottom: 1px solid #cbd5e1;">Reporte de faltantes</td>
            `;
            // Days 1-31
            for (let d = 1; d <= 31; d++) {
                if (d <= daysInMonth) {
                    const status = reportData.faltantes && reportData.faltantes[d] ? reportData.faltantes[d].status : null;
                    const comment = reportData.faltantes && reportData.faltantes[d] ? reportData.faltantes[d].comment : '';
                    html += createCell('faltantes', emp.id, d, status, comment, d, 'min-width: 30px;');
                } else {
                    html += `<td style="background: #f1f5f9; border-bottom: 1px solid #cbd5e1;"></td>`;
                }
            }
            html += '</tr>';

            // --- ROW 3: Reporte de Guías (Quincenal - 2 cells) ---
            html += `
                <tr>
                    <td style="padding: 0.3rem; background: #f1f5f9; font-size: 0.85rem; font-weight: 500; min-width: 150px; border-bottom: 1px solid #cbd5e1;">Reporte de guías y envió</td>
            `;
            // 2 cells spanning half month each roughly. 
            // 1st Quincena (Days 1-15), 2nd Quincena (16-End)
            // We use cellId 1 and 2
            const q1Status = reportData.guias && reportData.guias[1] ? reportData.guias[1].status : null;
            const q1Comment = reportData.guias && reportData.guias[1] ? reportData.guias[1].comment : '';

            const q2Status = reportData.guias && reportData.guias[2] ? reportData.guias[2].status : null;
            const q2Comment = reportData.guias && reportData.guias[2] ? reportData.guias[2].comment : '';

            html += createCell('guias', emp.id, 1, q1Status, q1Comment, '1 Quincena', `colspan="15"`, true);
            html += `<td style="border-bottom: 1px solid #cbd5e1; background: #e2e8f0; width: 4px;"></td>`; // Spacer
            html += createCell('guias', emp.id, 2, q2Status, q2Comment, '2 Quincena', `colspan="${Math.max(1, 31 - 15)}"`, true); // Span remaining

            // Pad if necessary (though colspan handles it mostly, strict grid might need empty cells if we used single cells. Here we use colspan)
            // Actually, previous row had 32 columns (1 label + 31 days). 
            // This row: 1 label + 15 + 1 + remaining. Total = 1 + 15 + 1 + (15 or 16) = 32 approx. 
            // Wait, 31 cells + 1 label = 32 columns.
            // Colspan 15 covers 1-15. Spacer covers 1? Remaining covers ~15.
            html += '</tr>';

            // --- ROW 4: Evidencia de tableros y bitacora (Weekly - 4 cells) ---
            html += `
                <tr>
                    <td style="padding: 0.3rem; background: #f1f5f9; font-size: 0.85rem; font-weight: 500; min-width: 150px; border-bottom: 2px solid #94a3b8;">Evidencia de tableros y bitacora</td>
            `;
            // 4 cells. 31 / 4 = ~7.75. Let's do spans of 7, 8, 8, 8 or similar.
            // Week 1: 1-7
            // Week 2: 8-15
            // Week 3: 16-23
            // Week 4: 24-End
            const weeks = [
                { id: 1, span: 7, label: '1 Semana' },
                { id: 2, span: 8, label: '2 Semana' },
                { id: 3, span: 8, label: '3 Semana' },
                { id: 4, span: 8, label: '4 Semana' } // 7+8+8+8 = 31
            ];

            weeks.forEach((w, idx) => {
                const st = reportData.tableros && reportData.tableros[w.id] ? reportData.tableros[w.id].status : null;
                const cm = reportData.tableros && reportData.tableros[w.id] ? reportData.tableros[w.id].comment : '';
                html += createCell('tableros', emp.id, w.id, st, cm, w.label, `colspan="${w.span}"`, true);
                if (idx < 3) {
                    // html += `<td style="border-bottom: 2px solid #94a3b8; background: #e2e8f0; width: 2px;"></td>`;
                    // Actually let's just use borders on the cells
                }
            });
            html += '</tr>';
        });

        document.getElementById('reportsBody').innerHTML = html;

    } catch (e) {
        console.error(e);
        document.getElementById('reportsBody').innerHTML = '<tr><td style="padding:2rem;">Error cargando datos.</td></tr>';
    }
}

function createCell(type, empId, key, status, comment, label, attrs = '', showLabel = false) {
    let content = '';
    let bgClass = '';

    if (status === 'check') {
        content = '✅';
        bgClass = 'bg-green-50';
    } else if (status === 'cross') {
        content = '❌';
        bgClass = 'bg-red-50';
    } else {
        content = ''; // Empty
    }

    const tooltip = comment ? `title="${comment.replace(/"/g, '&quot;')}"` : '';
    const hasComment = !!comment;
    const labelHtml = showLabel ? `<div style="font-size: 0.7rem; color: #64748b; margin-bottom: 4px;">${label}</div>` : `<div style="font-size: 0.7rem; color: #64748b; margin-bottom: 2px;">${label}</div>`; // Label for days too? Maybe just number

    // If it's a "faltantes" daily cell, label is just the number, maybe cleaner strictly inside query?
    // For daily, label is passed as just number "1", "2".

    return `
        <td ${attrs} 
            onclick="openReportSelection('${type}', ${empId}, ${key}, '${status || 'empty'}', '${comment ? comment.replace(/'/g, "\\'") : ''}')"
            ${tooltip}
            style="text-align: center; border: 1px solid #e2e8f0; border-bottom: ${type === 'tableros' ? '2px solid #94a3b8' : '1px solid #cbd5e1'}; cursor: pointer; position: relative; height: ${showLabel ? '60px' : '40px'}; min-width: ${showLabel ? '120px' : '40px'}; vertical-align: middle; background: ${status === 'check' ? '#f0fdf4' : status === 'cross' ? '#fef2f2' : 'white'}; user-select: none;">
            
            ${showLabel ? labelHtml : `<span style="position: absolute; top: 2px; left: 2px; font-size: 0.6rem; color: #94a3b8;">${label}</span>`}
            
            <div style="font-size: 1.2rem; line-height: 1; min-height: 20px;">${content}</div>
            ${hasComment ? '<div style="position: absolute; top: 4px; right: 4px; width: 6px; height: 6px; background: #f59e0b; border-radius: 50%;"></div>' : ''}
        </td>
    `;
}

// --- Interaction Logic ---
let pendingAction = null;

function openReportSelection(type, empId, key, currentStatus, currentComment) {
    // Store current cell info
    pendingAction = { type, empId, key, currentStatus, currentComment };

    // Show selection modal
    document.getElementById('reportSelectionModal').style.display = 'flex';
}

function closeReportSelection() {
    document.getElementById('reportSelectionModal').style.display = 'none';
    pendingAction = null;
}

function selectReportStatus(selectedStatus) {
    if (!pendingAction) return;

    const { type, empId, key } = pendingAction;

    // Close selection modal
    closeReportSelection();

    if (selectedStatus === 'cross') {
        // Open comment modal for cross/equis
        pendingAction = { type, empId, key, status: 'cross' };
        document.getElementById('reportCommentInput').value = '';
        document.getElementById('reportCommentModal').style.display = 'flex';
        document.getElementById('reportCommentInput').focus();
    } else if (selectedStatus === 'empty') {
        // Clear the cell
        saveReportUpdate(type, empId, key, 'empty', '');
    } else {
        // Save check/palomita immediately
        saveReportUpdate(type, empId, key, selectedStatus, '');
    }
}

function closeReportComment(save) {
    const modal = document.getElementById('reportCommentModal');
    modal.style.display = 'none';

    if (save && pendingAction) {
        const comment = document.getElementById('reportCommentInput').value;
        saveReportUpdate(pendingAction.type, pendingAction.empId, pendingAction.key, 'cross', comment);
    }
    pendingAction = null;
}

async function saveReportUpdate(type, empId, key, status, comment) {
    try {
        await fetch(`${API_BASE_URL}/reports`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                employee_id: empId,
                month: currentMonth,
                year: currentYear,
                type: type,
                key: key,
                status: status,
                comment: comment
            })
        });
        fetchAndRenderReports(); // Optimize: Local update? For now full refresh is safer
    } catch (e) {
        console.error(e);
        showToast('Error al guardar cambio', 'error');
    }
}

// Load specific month data
function loadReportsMonthData(month, year) {
    currentMonth = month;
    currentYear = year;
    loadReportes();
}

// Load current month
function loadCurrentReportsMonth() {
    const today = new Date();
    currentMonth = today.getMonth();
    currentYear = today.getFullYear();
    loadReportes();
}

