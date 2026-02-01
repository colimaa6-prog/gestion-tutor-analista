// ==================== BRANCH CHANGES (ROTACIÓN DE PERSONAL) ====================

let branchChangesPollingInterval = null;
let lastBranchChangesCount = 0;
const rotationSound = new Audio('death.mp3');

// Iniciar polling de cambios en sucursales
function startBranchChangesPolling() {
    // Poll cada 30 segundos
    branchChangesPollingInterval = setInterval(checkBranchChanges, 30000);
    // Verificar inmediatamente
    checkBranchChanges();
}

// Verificar cambios en sucursales
async function checkBranchChanges() {
    try {
        const userStr = sessionStorage.getItem('user');
        const user = userStr ? JSON.parse(userStr) : null;

        if (!user) return;

        const response = await fetch(`${API_BASE_URL}/branch-changes?userId=${user.id}`);
        const result = await response.json();

        if (result.success) {
            const changes = result.data || [];
            const count = changes.length;

            // Actualizar badge
            const badge = document.getElementById('rotationBadge');
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'flex';

                // Si hay nuevos cambios, reproducir sonido
                if (count > lastBranchChangesCount && lastBranchChangesCount > 0) {
                    rotationSound.play().catch(e => console.log('No se pudo reproducir el sonido'));
                }
            } else {
                badge.style.display = 'none';
            }

            lastBranchChangesCount = count;
        }
    } catch (error) {
        console.error('Error checking branch changes:', error);
    }
}

// Abrir panel de cambios en sucursales
async function openBranchChangesPanel() {
    try {
        const userStr = sessionStorage.getItem('user');
        const user = userStr ? JSON.parse(userStr) : null;

        if (!user) return;

        // Crear modal si no existe
        if (!document.getElementById('branchChangesModal')) {
            document.body.insertAdjacentHTML('beforeend', `
                <div id="branchChangesModal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.5); justify-content: center; align-items: center; z-index: 10002;">
                    <div style="background: white; padding: 2rem; border-radius: 12px; width: 700px; max-width: 90%; max-height: 90vh; display: flex; flex-direction: column;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 2px solid #f59e0b;">
                            <h3 style="margin: 0; color: #1e293b; display: flex; align-items: center; gap: 0.5rem;">
                                <img src="rotacion.png" alt="Rotación" style="height: 24px; width: auto;">
                                Cambios en sucursales
                            </h3>
                            <button onclick="closeBranchChangesPanel()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #64748b;">&times;</button>
                        </div>
                        
                        <div id="branchChangesList" style="overflow-y: auto; flex: 1; max-height: 500px;">
                            <p style="text-align: center; color: #94a3b8; padding: 1rem;">Cargando...</p>
                        </div>
                        
                        <div style="margin-top: 1rem; text-align: right;">
                            <button onclick="closeBranchChangesPanel()" style="padding: 0.6rem 1.2rem; background: #f1f5f9; color: #475569; border: none; border-radius: 6px; cursor: pointer;">Cerrar</button>
                        </div>
                    </div>
                </div>
            `);
        }

        // Mostrar modal
        document.getElementById('branchChangesModal').style.display = 'flex';

        // Cargar cambios
        const response = await fetch(`${API_BASE_URL}/branch-changes?userId=${user.id}`);
        const result = await response.json();

        if (result.success) {
            renderBranchChanges(result.data || []);
        } else {
            document.getElementById('branchChangesList').innerHTML = '<p style="text-align: center; color: #ef4444; padding: 1rem;">Error al cargar cambios</p>';
        }
    } catch (error) {
        console.error('Error opening branch changes panel:', error);
        document.getElementById('branchChangesList').innerHTML = '<p style="text-align: center; color: #ef4444; padding: 1rem;">Error de conexión</p>';
    }
}

// Cerrar panel
function closeBranchChangesPanel() {
    document.getElementById('branchChangesModal').style.display = 'none';
}

// Renderizar lista de cambios
function renderBranchChanges(changes) {
    const container = document.getElementById('branchChangesList');

    if (changes.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #94a3b8; padding: 2rem;">No hay cambios pendientes</p>';
        return;
    }

    let html = '<div style="display: flex; flex-direction: column; gap: 0.75rem;">';

    changes.forEach(change => {
        const isIngreso = change.change_type === 'ingreso';
        const bgColor = isIngreso ? '#d1fae5' : '#fee2e2';
        const textColor = isIngreso ? '#065f46' : '#991b1b';
        const icon = isIngreso ? '✓' : '✗';

        html += `
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; position: relative; border-left: 4px solid ${isIngreso ? '#10b981' : '#ef4444'};">
                <div style="display: flex; justify-content: space-between; align-items: start; gap: 1rem;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="background: ${bgColor}; color: ${textColor}; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                                ${icon} ${isIngreso ? 'INGRESO' : 'EGRESO'}
                            </span>
                            <span style="color: #64748b; font-size: 0.75rem;">${change.created_at}</span>
                        </div>
                        
                        <div style="color: #1e293b; font-weight: 500; margin-bottom: 0.25rem;">
                            ${change.branch_name || 'Sucursal desconocida'}
                        </div>
                        
                        ${change.description ? `
                            <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem; padding: 0.5rem; background: #f8fafc; border-radius: 4px;">
                                ${change.description}
                            </div>
                        ` : ''}
                        
                        ${change.employee_name ? `
                            <div style="color: #475569; font-size: 0.85rem; margin-top: 0.5rem;">
                                <strong>Colaborador:</strong> ${change.employee_name}
                                ${change.hire_date ? ` | <strong>Fecha:</strong> ${change.hire_date}` : ''}
                            </div>
                        ` : ''}
                    </div>
                    
                    <button onclick="processBranchChange(${change.id})" 
                            style="background: #ef4444; color: white; border: none; width: 28px; height: 28px; border-radius: 50%; cursor: pointer; font-size: 1.2rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: background 0.2s;"
                            onmouseover="this.style.background='#dc2626'"
                            onmouseout="this.style.background='#ef4444'"
                            title="Marcar como procesado">
                        ×
                    </button>
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

// Procesar (eliminar) un cambio
async function processBranchChange(changeId) {
    try {
        const userStr = sessionStorage.getItem('user');
        const user = userStr ? JSON.parse(userStr) : null;

        if (!user) return;

        const response = await fetch(`${API_BASE_URL}/branch-changes/${changeId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ userId: user.id })
        });

        const result = await response.json();

        if (result.success) {
            showToast('Cambio procesado correctamente', 'success');
            // Recargar lista
            openBranchChangesPanel();
            // Actualizar contador
            checkBranchChanges();
        } else {
            showToast('Error al procesar cambio', 'error');
        }
    } catch (error) {
        console.error('Error processing branch change:', error);
        showToast('Error de conexión', 'error');
    }
}
