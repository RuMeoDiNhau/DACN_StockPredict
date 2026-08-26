// Main JavaScript cho Stock AI Predictor
// Quản lý các tính năng chung của ứng dụng

// Biến global
let currentSymbol = 'VHM';
let priceChart = null;

// Khởi tạo khi trang load
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Khởi tạo ứng dụng
 */
function initializeApp() {
    console.log('🚀 Khởi tạo Stock AI Predictor');
    
    // Kiểm tra hỗ trợ localStorage
    checkBrowserSupport();
    
    // Setup event listeners chung
    setupGlobalEventListeners();
    
    // Load market status
    loadMarketStatus();
    
    // Auto refresh market data mỗi 5 phút
    setInterval(loadMarketStatus, 5 * 60 * 1000);
}

/**
 * Kiểm tra hỗ trợ trình duyệt
 */
function checkBrowserSupport() {
    // Kiểm tra localStorage
    if (!window.localStorage) {
        showAlert('Trình duyệt không hỗ trợ localStorage', 'warning');
    }
    
    // Kiểm tra fetch API
    if (!window.fetch) {
        showAlert('Trình duyệt không hỗ trợ Fetch API', 'error');
    }
    
    // Kiểm tra Chart.js
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js chưa được load');
    }
}

/**
 * Setup event listeners chung
 */
function setupGlobalEventListeners() {
    // Handle form submissions
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.classList.contains('ajax-form')) {
            e.preventDefault();
            handleAjaxForm(form);
        }
    });
    
    // Handle AJAX buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('ajax-btn')) {
            e.preventDefault();
            handleAjaxButton(e.target);
        }
    });
}

/**
 * Load market status
 */
async function loadMarketStatus() {
    try {
        const response = await fetch('/api/market-status');
        const data = await response.json();
        
        if (data.success) {
            updateMarketStatusUI(data.status);
        }
    } catch (error) {
        console.error('❌ Lỗi load market status:', error);
    }
}

/**
 * Update market status UI
 */
function updateMarketStatusUI(status) {
    const statusElement = document.getElementById('market-status');
    if (!statusElement) return;
    
    const isOpen = status.is_open;
    const statusClass = isOpen ? 'success' : 'danger';
    const statusText = isOpen ? 'mở' : 'đóng';
    
    statusElement.innerHTML = `
        <i class="fas fa-circle text-${statusClass}"></i>
        Thị trường ${statusText}
    `;
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alert-container') || createAlertContainer();
    
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger', 
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show auto-hide" role="alert">
            <i class="fas fa-${getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto remove after duration
    if (duration > 0) {
        setTimeout(() => {
            const alert = alertContainer.lastElementChild;
            if (alert && alert.classList.contains('auto-hide')) {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 150);
            }
        }, duration);
    }
}

/**
 * Create alert container if not exists
 */
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

/**
 * Get alert icon based on type
 */
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Format currency in Vietnamese style
 */
function formatCurrency(amount, currency = 'VND') {
    if (currency === 'VND') {
        return new Intl.NumberFormat('vi-VN').format(amount) + ' ₫';
    }
    return new Intl.NumberFormat('vi-VN').format(amount) + ' ' + currency;
}

/**
 * Format percentage
 */
function formatPercentage(value, decimals = 2) {
    const percentage = (value * 100).toFixed(decimals);
    return (value >= 0 ? '+' : '') + percentage + '%';
}

// Export functions for use in other scripts
window.StockApp = {
    showAlert,
    formatCurrency,
    formatPercentage,
    loadMarketStatus
};