let currentSymbol = null;
let allRows = [];
let selectedPeriod = 30;

const byId = (id) => document.getElementById(id);

document.addEventListener('DOMContentLoaded', async () => {
  bindControls();
  await loadMarketStatus();
  if (document.body.dataset.page === 'symbol') {
    const symbol = window.location.pathname.split('/').pop();
    await loadSymbol(symbol);
  } else {
    await loadSymbols();
  }
});

function bindControls() {
  const form = byId('symbol-form');
  if (form) form.addEventListener('submit', (event) => {
    event.preventDefault();
    const symbol = byId('symbol-search').value.trim().toUpperCase();
    if (symbol) window.location.assign(`/symbol/${encodeURIComponent(symbol)}`);
  });
  document.querySelectorAll('[data-period]').forEach((button) => button.addEventListener('click', () => {
    selectedPeriod = Number(button.dataset.period);
    document.querySelectorAll('[data-period]').forEach((item) => item.classList.toggle('active', item === button));
    renderOhlcv(allRows.slice(-selectedPeriod));
  }));
}

async function api(path) {
  const response = await fetch(path, { headers: { Accept: 'application/json' } });
  const payload = await response.json().catch(() => ({ success: false, error: 'Invalid API response' }));
  if (!response.ok || !payload.success) throw new Error(payload.error || `HTTP ${response.status}`);
  return payload;
}

async function loadSymbols() {
  setStatus('symbols-status', 'Đang tải danh sách mã…');
  try {
    const payload = await api('/api/symbols');
    const list = byId('symbols-list');
    list.replaceChildren();
    if (!payload.symbols.length) {
      setStatus('symbols-status', 'SQLite chưa có dữ liệu. Hãy chạy collector để nạp OHLCV.', 'error');
      return;
    }
    setStatus('symbols-status', `${payload.symbols.length} mã có dữ liệu.`, 'success');
    payload.symbols.forEach((symbol) => {
      const item = document.createElement('li'); const button = document.createElement('button');
      button.textContent = symbol; button.addEventListener('click', () => window.location.assign(`/symbol/${encodeURIComponent(symbol)}`));
      item.append(button); list.append(item);
    });
    await loadSymbol(payload.symbols[0]);
  } catch (error) { setStatus('symbols-status', error.message, 'error'); }
}

async function loadSymbol(symbol) {
  currentSymbol = String(symbol).trim().toUpperCase();
  byId('current-symbol').textContent = currentSymbol;
  const dashboardLink = byId('dashboard-link'); if (dashboardLink) dashboardLink.href = `/?symbol=${encodeURIComponent(currentSymbol)}`;
  setStatus('ohlcv-status', `Đang tải ${currentSymbol}…`);
  try {
    const payload = await api(`/api/stocks/${encodeURIComponent(currentSymbol)}?limit=90`);
    allRows = payload.data;
    renderOhlcv(allRows.slice(-selectedPeriod));
    setStatus('ohlcv-status', `Đã tải ${allRows.length} phiên OHLCV.`, 'success');
  } catch (error) { allRows = []; renderOhlcv([]); setStatus('ohlcv-status', error.message, 'error'); }
}

function renderOhlcv(rows) {
  renderChart(rows);
  const latest = rows.at(-1);
  if (byId('latest-date')) byId('latest-date').textContent = latest ? latest.Date.slice(0, 10) : '—';
  if (byId('latest-close')) byId('latest-close').textContent = latest ? formatNumber(latest.Close) : '—';
  if (byId('latest-volume')) byId('latest-volume').textContent = latest ? formatNumber(latest.Volume) : '—';
  const body = byId('ohlcv-table');
  if (body) body.innerHTML = rows.map((row) => `<tr><td>${row.Date.slice(0, 10)}</td><td>${formatNumber(row.Open)}</td><td>${formatNumber(row.High)}</td><td>${formatNumber(row.Low)}</td><td>${formatNumber(row.Close)}</td><td>${formatNumber(row.Volume)}</td><td>${row.Symbol}</td></tr>`).join('');
}

function renderChart(rows) {
  const chart = byId('chart'); if (!chart) return;
  if (!rows.length) { chart.textContent = 'Chưa có dữ liệu OHLCV để hiển thị.'; return; }
  const values = rows.map((row) => Number(row.Close)); const min = Math.min(...values); const max = Math.max(...values); const range = max - min || 1;
  const points = values.map((value, index) => `${(index / Math.max(values.length - 1, 1)) * 100},${100 - ((value - min) / range) * 100}`).join(' ');
  chart.innerHTML = `<svg viewBox="0 0 100 100" preserveAspectRatio="none"><polyline points="${points}"/><text x="1" y="10">${formatNumber(max)}</text><text x="1" y="96">${formatNumber(min)}</text></svg>`;
}

async function loadMarketStatus() {
  try { const status = await api('/api/market-status'); byId('market-status').textContent = `Thị trường ${status.is_open ? 'mở' : 'đóng'} (${status.timezone})`; }
  catch (_) { byId('market-status').textContent = 'Không tải được trạng thái thị trường'; }
}

function setStatus(id, message, kind = '') { const element = byId(id); if (element) { element.textContent = message; element.className = `status ${kind}`; } }
function formatNumber(value) { return new Intl.NumberFormat('vi-VN').format(Number(value)); }
