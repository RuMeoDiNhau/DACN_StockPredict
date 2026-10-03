let currentSymbol = 'VHM';
let priceChart = null;
let currentRows = [];

document.addEventListener('DOMContentLoaded', initializeApp);

function initializeApp() {
    setupGlobalEventListeners();
    loadMarketStatus();
    const firstSymbol = document.querySelector('.symbol-item');
    if (firstSymbol) {
        selectSymbol(firstSymbol.dataset.symbol);
    } else {
        setOhlcvStatus('ChÆ°a cÃ³ mÃ£ nÃ o cÃ³ dá»¯ liá»‡u trong SQLite.', 'muted');
    }
    setInterval(loadMarketStatus, 5 * 60 * 1000);
}

function setupGlobalEventListeners() {
    document.querySelectorAll('.symbol-item').forEach(item => {
        item.addEventListener('click', event => {
            event.preventDefault();
            selectSymbol(item.dataset.symbol);
        });
    });
    document.querySelectorAll('[data-period]').forEach(button => {
        button.addEventListener('click', () => {
            document.querySelectorAll('[data-period]').forEach(item => item.classList.remove('active'));
            button.classList.add('active');
            renderRows(currentRows.slice(-Number(button.dataset.period)));
        });
    });
    const search = document.getElementById('symbol-search');
    if (search) {
        search.addEventListener('input', () => {
            const query = search.value.trim().toUpperCase();
            document.querySelectorAll('.symbol-item').forEach(item => {
                item.classList.toggle('d-none', !item.dataset.symbol.includes(query));
            });
        });
    }
}

async function selectSymbol(symbol) {
    currentSymbol = symbol.toUpperCase();
    const heading = document.getElementById('current-symbol');
    if (heading) heading.textContent = currentSymbol;
    setOhlcvStatus(`Äang táº£i dá»¯ liá»‡u ${currentSymbol}...`, 'muted');
    try {
        const response = await fetch(`/api/stocks/${encodeURIComponent(currentSymbol)}?limit=90`);
        const payload = await response.json();
        if (!response.ok || !payload.success) throw new Error(payload.error || 'KhÃ´ng táº£i Ä‘Æ°á»£c dá»¯ liá»‡u');
        currentRows = payload.data || [];
        renderRows(currentRows.slice(-getSelectedPeriod()));
        setOhlcvStatus(`ÄÃ£ táº£i ${currentRows.length} phiÃªn`, 'success');
    } catch (error) {
        currentRows = [];
        renderRows([]);
        setOhlcvStatus(error.message, 'error');
    }
}

function getSelectedPeriod() {
    const active = document.querySelector('[data-period].active');
    return active ? Number(active.dataset.period) : 30;
}

function renderRows(rows) {
    const latest = rows[rows.length - 1];
    document.getElementById('latest-date').textContent = latest ? formatDate(latest.Date) : '--';
    document.getElementById('latest-close').textContent = latest ? formatNumber(latest.Close) : '--';
    document.getElementById('latest-volume').textContent = latest ? formatNumber(latest.Volume) : '--';
    if (typeof Chart === 'undefined') return;
    const canvas = document.getElementById('price-chart');
    if (!canvas) return;
    if (priceChart) priceChart.destroy();
    priceChart = new Chart(canvas, {
        type: 'line',
        data: {
            labels: rows.map(row => formatDate(row.Date)),
            datasets: [{ label: `${currentSymbol} Close`, data: rows.map(row => row.Close), borderColor: '#0d6efd', tension: 0.2 }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

async function loadMarketStatus() {
    try {
        const response = await fetch('/api/market-status');
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error('Market status unavailable');
        updateMarketStatusUI(data);
    } catch (error) {
        updateMarketStatusUI({is_open: false, status: 'unavailable'});
    }
}

function updateMarketStatusUI(status) {
    const element = document.getElementById('market-status');
    if (!element) return;
    const open = status.is_open;
    element.innerHTML = `<i class="fas fa-circle text-${open ? 'success' : 'secondary'}"></i> Thá»‹ trÆ°á»ng ${open ? 'má»Ÿ' : 'Ä‘Ã³ng'}`;
}

function setOhlcvStatus(message, type) {
    const element = document.getElementById('ohlcv-status');
    if (!element) return;
    element.textContent = message;
    element.className = `mb-2 text-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'muted'}`;
}

function formatDate(value) { return String(value).slice(0, 10); }
function formatNumber(value) { return new Intl.NumberFormat('vi-VN').format(Number(value)); }
function formatCurrency(amount, currency = 'VND') { return formatNumber(amount) + ` ${currency}`; }
function formatPercentage(value, decimals = 2) { return `${value >= 0 ? '+' : ''}${(value * 100).toFixed(decimals)}%`; }
function showAlert(message) { window.alert(message); }

window.StockApp = { showAlert, formatCurrency, formatPercentage, loadMarketStatus, selectSymbol };
