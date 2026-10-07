let currentSymbol = null;
let allRows = [];
let selectedPeriod = 30;
let tableExpanded = false;

const byId = (id) => document.getElementById(id);
const numberFormat = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 });
const integerFormat = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 0 });

document.addEventListener('DOMContentLoaded', async () => {
  bindControls();
  await loadMarketStatus();
  if (document.body.dataset.page === 'symbol') {
    const symbol = decodeURIComponent(window.location.pathname.split('/').pop() || '');
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
    renderChart(allRows.slice(-selectedPeriod));
  }));
  const toggle = byId('toggle-table');
  if (toggle) toggle.addEventListener('click', () => {
    tableExpanded = !tableExpanded;
    renderTable();
  });
}

async function api(path) {
  const response = await fetch(path, { headers: { Accept: 'application/json' } });
  const payload = await response.json().catch(() => ({ success: false, error: 'Invalid API response' }));
  if (!response.ok || !payload.success) {
    const error = new Error(payload.error || `HTTP ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return payload;
}

async function loadSymbols() {
  setStatus('symbols-status', 'Đang tải danh sách mã…');
  try {
    const payload = await api('/api/symbols');
    const list = byId('symbols-list');
    list.replaceChildren();
    if (!payload.symbols.length) {
      setStatus('symbols-status', 'Chưa có dữ liệu trong SQLite. Hãy chạy collector để nạp OHLCV.', 'error');
      return;
    }
    setStatus('symbols-status', `${payload.symbols.length} mã có dữ liệu.`, 'success');
    payload.symbols.forEach((symbol) => {
      const item = document.createElement('li');
      const button = document.createElement('button');
      button.textContent = symbol;
      button.addEventListener('click', () => window.location.assign(`/symbol/${encodeURIComponent(symbol)}`));
      item.append(button);
      list.append(item);
    });
    await loadSymbol(payload.symbols[0]);
  } catch (error) {
    setStatus('symbols-status', 'Không thể tải danh sách mã. Vui lòng thử lại.', 'error');
  }
}

async function loadSymbol(symbol) {
  currentSymbol = String(symbol).trim().toUpperCase();
  const heading = byId('current-symbol');
  if (heading) heading.textContent = currentSymbol || 'Mã cổ phiếu';
  const dashboardLink = byId('dashboard-link');
  if (dashboardLink) dashboardLink.href = `/?symbol=${encodeURIComponent(currentSymbol)}`;
  document.body.classList.add('loading');
  setStatus('ohlcv-status', `Đang tải dữ liệu ${currentSymbol}…`);
  try {
    const payload = await api(`/api/stocks/${encodeURIComponent(currentSymbol)}?limit=90`);
    allRows = Array.isArray(payload.data) ? payload.data : [];
    tableExpanded = false;
    renderSummary(allRows);
    renderChart(allRows.slice(-selectedPeriod));
    renderTable();
    if (!allRows.length) {
      setStatus('ohlcv-status', 'Mã này chưa có dữ liệu OHLCV.', 'error');
    } else {
      setStatus('ohlcv-status', `Đã tải ${allRows.length} phiên OHLCV.`, 'success');
    }
  } catch (error) {
    allRows = [];
    renderSummary([]);
    renderChart([]);
    renderTable();
    setStatus(
      'ohlcv-status',
      error.status === 404 ? `Chưa có dữ liệu cho mã ${currentSymbol}.` : 'Không thể tải dữ liệu. Vui lòng thử lại.',
      'error'
    );
  } finally {
    document.body.classList.remove('loading');
  }
}

function renderSummary(rows) {
  const latest = rows[rows.length - 1];
  const previous = rows.length > 1 ? rows[rows.length - 2] : null;
  const setText = (id, value) => { if (byId(id)) byId(id).textContent = value; };
  setText('summary-count', rows.length ? `${rows.length} phiên` : '—');
  setText('summary-range', rows.length ? `${formatDate(rows[0].Date)} – ${formatDate(latest.Date)}` : '—');
  setText('summary-latest-date', latest ? formatDate(latest.Date) : '—');
  setText('summary-close', latest ? `${formatPrice(latest.Close)} nghìn VNĐ` : '—');
  const change = byId('summary-change');
  if (!change) return;
  change.className = 'neutral';
  if (!latest || !previous) {
    change.textContent = 'Chưa đủ dữ liệu';
    return;
  }
  const difference = Number(latest.Close) - Number(previous.Close);
  const percent = Number(previous.Close) ? (difference / Number(previous.Close)) * 100 : null;
  const sign = difference > 0 ? '+' : '';
  change.className = difference > 0 ? 'positive' : difference < 0 ? 'negative' : 'neutral';
  change.textContent = `${sign}${formatPrice(difference)} (${percent === null ? '—' : `${sign}${formatPrice(percent)}%`})`;
}

function renderTable() {
  const body = byId('ohlcv-table');
  if (!body) return;
  body.replaceChildren();
  const rows = allRows.slice().reverse();
  const visibleRows = tableExpanded ? rows : rows.slice(0, 20);
  visibleRows.forEach((row) => {
    const tr = document.createElement('tr');
    [formatDate(row.Date), formatPrice(row.Open), formatPrice(row.High), formatPrice(row.Low), formatPrice(row.Close), formatVolume(row.Volume)]
      .forEach((value, index) => {
        const cell = document.createElement('td');
        cell.textContent = value;
        if (index > 0) cell.className = 'number-cell';
        tr.append(cell);
      });
    body.append(tr);
  });
  const toggle = byId('toggle-table');
  if (toggle) {
    toggle.hidden = rows.length <= 20;
    toggle.textContent = tableExpanded ? 'Thu gọn' : `Xem thêm (${rows.length - 20})`;
  }
}

function renderChart(rows) {
  const chart = byId('chart');
  if (!chart) return;
  const tooltip = byId('chart-tooltip');
  if (tooltip) tooltip.classList.remove('visible');
  if (!rows.length) {
    chart.innerHTML = '<div class="chart-empty">Chưa có dữ liệu OHLCV để hiển thị.</div>';
    return;
  }

  const width = 800; const height = 320;
  const left = 62; const right = 18; const top = 24; const bottom = 48;
  const plotWidth = width - left - right; const plotHeight = height - top - bottom;
  const values = rows.map((row) => Number(row.Close));
  const minValue = Math.min(...values); const maxValue = Math.max(...values);
  const padding = (maxValue - minValue || Math.max(maxValue * 0.02, 1)) * 0.12;
  const min = Math.max(0, minValue - padding); const max = maxValue + padding; const range = max - min || 1;
  const x = (index) => left + (index / Math.max(rows.length - 1, 1)) * plotWidth;
  const y = (value) => top + (1 - (value - min) / range) * plotHeight;
  const points = values.map((value, index) => `${x(index)},${y(value)}`).join(' ');
  const grid = [0, 1, 2, 3, 4].map((step) => {
    const value = min + (range * step) / 4; const lineY = y(value);
    return `<line class="chart-grid" x1="${left}" y1="${lineY}" x2="${width - right}" y2="${lineY}"/><text class="chart-axis-label" x="${left - 8}" y="${lineY + 4}" text-anchor="end">${formatPrice(value)}</text>`;
  }).join('');
  const labelIndexes = [...new Set([0, Math.floor((rows.length - 1) / 2), rows.length - 1])];
  const xLabels = labelIndexes.map((index) => `<text class="chart-axis-label" x="${x(index)}" y="${height - 16}" text-anchor="middle">${formatDate(rows[index].Date)}</text>`).join('');
  const pointsMarkup = rows.map((row, index) => `<circle class="chart-point" cx="${x(index)}" cy="${y(Number(row.Close))}" r="${rows.length < 3 ? 5 : 4}" data-index="${index}" tabindex="0" aria-label="${formatDate(row.Date)}: ${formatPrice(row.Close)}"/>`).join('');
  chart.innerHTML = `<svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-label="Biểu đồ giá đóng cửa của ${currentSymbol}"><g>${grid}${xLabels}<polyline class="chart-line" points="${points}"/>${pointsMarkup}</g></svg>`;
  chart.querySelectorAll('.chart-point').forEach((point) => {
    point.addEventListener('mouseenter', (event) => showTooltip(rows[Number(event.currentTarget.dataset.index)], event));
    point.addEventListener('focus', (event) => showTooltip(rows[Number(event.currentTarget.dataset.index)], event));
    point.addEventListener('mouseleave', hideTooltip);
    point.addEventListener('blur', hideTooltip);
  });
}

function showTooltip(row, event) {
  const tooltip = byId('chart-tooltip'); const section = document.querySelector('.chart-section');
  if (!tooltip || !section || !row) return;
  tooltip.innerHTML = `<strong>${formatDate(row.Date)}</strong><span>Open: ${formatPrice(row.Open)}</span><span>High: ${formatPrice(row.High)}</span><span>Low: ${formatPrice(row.Low)}</span><span>Close: ${formatPrice(row.Close)}</span><span>Volume: ${formatVolume(row.Volume)}</span>`;
  tooltip.classList.add('visible');
  const rect = section.getBoundingClientRect();
  const clientX = event.clientX || rect.left + rect.width / 2;
  const clientY = event.clientY || rect.top + 80;
  tooltip.style.left = `${Math.min(Math.max(8, clientX - rect.left + 12), rect.width - tooltip.offsetWidth - 8)}px`;
  tooltip.style.top = `${Math.max(8, clientY - rect.top - tooltip.offsetHeight - 12)}px`;
}

function hideTooltip() { const tooltip = byId('chart-tooltip'); if (tooltip) tooltip.classList.remove('visible'); }
async function loadMarketStatus() {
  try { const status = await api('/api/market-status'); const element = byId('market-status'); if (element) element.textContent = `Thị trường ${status.is_open ? 'mở' : 'đóng'} (${status.timezone})`; }
  catch (_) { const element = byId('market-status'); if (element) element.textContent = 'Không tải được trạng thái thị trường'; }
}
function setStatus(id, message, kind = '') { const element = byId(id); if (element) { element.textContent = message; element.className = `status ${kind}`; } }
function formatDate(value) { return String(value || '').slice(0, 10) || '—'; }
function formatPrice(value) { return numberFormat.format(Number(value)); }
function formatVolume(value) { return integerFormat.format(Number(value)); }
