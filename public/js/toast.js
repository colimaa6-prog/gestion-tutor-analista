/**
 * Toast Notification System
 * Modern, accessible toast notifications to replace native browser dialogs
 */

// Toast icons mapping
const TOAST_ICONS = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️',
    confirm: '❓'
};

// Initialize toast container
function initToastContainer() {
    if (!document.getElementById('toastContainer')) {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.setAttribute('role', 'region');
        container.setAttribute('aria-label', 'Notificaciones');
        document.body.appendChild(container);
    }
}

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - Type of toast: 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duration in milliseconds (0 = no auto-dismiss)
 */
function showToast(message, type = 'info', duration = 4000) {
    initToastContainer();

    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    toast.id = toastId;
    toast.className = `toast ${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');

    const icon = TOAST_ICONS[type] || TOAST_ICONS.info;

    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-content">
            <div class="toast-message">${escapeHtml(message)}</div>
        </div>
        <button class="toast-close" onclick="dismissToast('${toastId}')" aria-label="Cerrar notificación">×</button>
        ${duration > 0 ? `<div class="toast-progress" style="animation-duration: ${duration}ms;"></div>` : ''}
    `;

    container.appendChild(toast);

    // Auto-dismiss for success/info toasts
    if (duration > 0) {
        setTimeout(() => {
            dismissToast(toastId);
        }, duration);
    }

    return toastId;
}

/**
 * Show a confirmation toast with action buttons
 * @param {string} message - The confirmation message
 * @param {Function} onConfirm - Callback when user confirms
 * @param {Function} onCancel - Callback when user cancels (optional)
 * @param {Object} options - Additional options
 */
function showConfirmToast(message, onConfirm, onCancel = null, options = {}) {
    initToastContainer();

    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    toast.id = toastId;
    toast.className = 'toast confirm';
    toast.setAttribute('role', 'alertdialog');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-labelledby', `${toastId}-message`);

    const confirmText = options.confirmText || 'Confirmar';
    const cancelText = options.cancelText || 'Cancelar';
    const icon = options.icon || TOAST_ICONS.confirm;

    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-content">
            <div class="toast-message" id="${toastId}-message">${escapeHtml(message)}</div>
            <div class="toast-actions">
                <button class="toast-btn toast-btn-confirm" id="${toastId}-confirm">${confirmText}</button>
                <button class="toast-btn toast-btn-cancel" id="${toastId}-cancel">${cancelText}</button>
            </div>
        </div>
    `;

    container.appendChild(toast);

    // Add event listeners
    const confirmBtn = document.getElementById(`${toastId}-confirm`);
    const cancelBtn = document.getElementById(`${toastId}-cancel`);

    confirmBtn.addEventListener('click', () => {
        dismissToast(toastId);
        if (onConfirm) onConfirm();
    });

    cancelBtn.addEventListener('click', () => {
        dismissToast(toastId);
        if (onCancel) onCancel();
    });

    // Focus on confirm button for accessibility
    setTimeout(() => confirmBtn.focus(), 100);

    // Keyboard support
    toast.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            dismissToast(toastId);
            if (onCancel) onCancel();
        }
    });

    return toastId;
}

/**
 * Dismiss a toast notification
 * @param {string} toastId - The ID of the toast to dismiss
 */
function dismissToast(toastId) {
    const toast = document.getElementById(toastId);
    if (!toast) return;

    toast.classList.add('removing');

    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300); // Match animation duration
}

/**
 * Dismiss all toasts
 */
function dismissAllToasts() {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toasts = container.querySelectorAll('.toast');
    toasts.forEach(toast => {
        dismissToast(toast.id);
    });
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Convenience methods for common toast types
const Toast = {
    success: (message, duration = 4000) => showToast(message, 'success', duration),
    error: (message, duration = 0) => showToast(message, 'error', duration),
    warning: (message, duration = 5000) => showToast(message, 'warning', duration),
    info: (message, duration = 4000) => showToast(message, 'info', duration),
    confirm: (message, onConfirm, onCancel, options) => showConfirmToast(message, onConfirm, onCancel, options),
    dismiss: (toastId) => dismissToast(toastId),
    dismissAll: () => dismissAllToasts()
};

// Make functions globally available
window.showToast = showToast;
window.showConfirmToast = showConfirmToast;
window.dismissToast = dismissToast;
window.dismissAllToasts = dismissAllToasts;
window.Toast = Toast;

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initToastContainer);
} else {
    initToastContainer();
}
