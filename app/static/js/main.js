// Funciones de JavaScript de Asadero Rossy Pollo

document.addEventListener('DOMContentLoaded', function() {
    // 1. INICIALIZAR MODO OSCURO / CLARO
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeToggleIcon(savedTheme);

    // Configurar listener para el botón de alternancia si existe
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }

    // 2. INICIALIZAR TOOLTIPS
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // 3. AUTO-CERRAR ALERTAS DE BOOTSTRAP SI EXISTEN
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                alert.style.display = 'none';
            }
        }, 5000);
    });
});

// ALTERNAR TEMA (CLARO/OSCURO)
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeToggleIcon(newTheme);
}

// ACTUALIZAR ICONO DE MODO OSCURO
function updateThemeToggleIcon(theme) {
    const icon = document.querySelector('#theme-toggle i');
    if (icon) {
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
            icon.style.color = '#e28f32';
        } else {
            icon.className = 'fas fa-moon';
            icon.style.color = '#6b5c51';
        }
    }
}

// MOSTRAR TOAST PERSONALIZADO PREMIUM
function showToast(message, type = 'info') {
    // Buscar o crear contenedor de toasts
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `custom-toast ${type}`;
    
    let iconClass = 'info-circle';
    if (type === 'success') iconClass = 'check-circle';
    if (type === 'error') iconClass = 'exclamation-circle';

    toast.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${iconClass} me-2"></i>
            <span>${message}</span>
        </div>
        <button type="button" class="btn-close ms-3 bg-transparent border-0" style="color: inherit;" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    // Auto-eliminar después de 4 segundos
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// LLAMADAS AJAX GENÉRICAS
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Ocurrió un error inesperado');
        }
        return data;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

// CONFIRMACIÓN Y ELIMINACIÓN DE POST POR AJAX
async function deletePost(postId, redirectUrl = '/dashboard') {
    // Usar SweetAlert2 si está disponible, de lo contrario un confirm estilizado
    const confirmDelete = confirm('¿Estás seguro de que deseas eliminar este artículo de forma permanente?');
    if (!confirmDelete) return;

    try {
        const response = await fetch(`/admin/post/${postId}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Post eliminado con éxito', 'success');
            setTimeout(() => {
                window.location.href = redirectUrl;
            }, 1000);
        } else {
            showToast(data.error || 'Error al eliminar el post', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error de conexión al eliminar el post', 'error');
    }
}
