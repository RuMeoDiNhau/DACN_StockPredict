let currentSymbol = null;
let availableSymbols = [];
let allRows = [];
let selectedPeriod = 30;
let tableExpanded = false;
let dashboardChart = null;
let dashboardChartObserver = null;

const byId = (id) => document.getElementById(id);
const numberFormat = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 });
const integerFormat = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 0 });

document.addEventListener('DOMContentLoaded', async () => {
  bindControls();
  await loadMarketStatus();
  if (document.body.dataset.page === 'dashboard') {
    await loadSymbols();
  } else {
    const symbol = decodeURIComponent(window.location.pathname.split('/').pop() || '');
    await loadSymbol(symbol);
  }
});

function bindControls() {
  const form = byId('symbol-form');
  if (form) form.addEventListener('submit', (event) => {
    event.preventDefault();
    const symbol = byId('symbol-search').value.trim().toUpperCase();
    if (symbol && isDashboard()) {
      window.history.replaceState({}, '', `/?symbol=${encodeURIComponent(symbol)}`);
      loadSymbol(symbol);
    } else if (symbol) window.location.assign(`/symbol/${encodeURIComponent(symbol)}`);
  });
  document.querySelectorAll('[data-period]').forEach((button) => button.addEventListener('click', () => {
    selectedPeriod = Number(button.dataset.period);
    document.querySelectorAll('[data-period]').forEach((item) => item.classList.toggle('active', item === button));
    if (isDashboard()) renderDashboardChart(allRows.slice(-selectedPeriod));
    else renderDetailChart(allRows.slice(-selectedPeriod));
  }));
  const toggle = byId('toggle-table');
  if (toggle) toggle.addEventListener('click', () => { tableExpanded = !tableExpanded; renderTable(); });
  const filter = byId('watchlist-filter');
  if (filter) filter.addEventListener('input', () => renderWatchlist(filter.value));
  window.addEventListener('beforeunload', disposeDashboardChart);
}

function isDashboard() { return document.body.dataset.page === 'dashboard'; }

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
  setStatus('watchlist-status', 'Đang tải danh sách mã…');
  try {
    const payload = await api('/api/symbols');
    availableSymbols = Array.isArray(payload.symbols) ? payload.symbols : [];
    const datalist = byId('symbol-options');
    if (datalist) {
      datalist.replaceChildren();
      availableSymbols.forEach((symbol) => { const option = document.createElement('option'); option.value = symbol; datalist.append(option); });
    }
    renderWatchlist();
    if (!availableSymbols.length) {
      setStatus('symbols-status', 'Chưa có dữ liệu trong SQLite. Hãy chạy collector để nạp OHLCV.', 'error');
      setStatus('watchlist-status', 'Watchlist trống vì database chưa có dữ liệu.', 'error');
      clearDashboardData();
      return;
    }
    setStatus('symbols-status', `${availableSymbols.length} mã có dữ liệu.`, 'success');
    setStatus('watchlist-status', '', '');
    const requested = new URLSearchParams(window.location.search).get('symbol');
    const symbol = requested && availableSymbols.includes(requested.toUpperCase()) ? requested.toUpperCase() : availableSymbols[0];
    await loadSymbol(symbol);
  } catch (error) {
    setStatus('symbols-status', 'Không thể tải danh sách mã. Vui lòng thử lại.', 'error');
    setStatus('watchlist-status', 'Không thể tải watchlist.', 'error');
    renderWatchlist();
    clearDashboardData();
  }
}

function renderWatchlist(filterText = '') {
  const list = byId('symbols-list');
  if (!list) return;
  const query = String(filterText).trim().toUpperCase();
  const filtered = availableSymbols.filter((symbol) => symbol.includes(query));
  list.replaceChildren();
  const count = byId('watchlist-count');
  if (count) count.textContent = String(availableSymbols.length);
  if (!filtered.length) {
    const empty = document.createElement('li'); empty.className = 'watchlist-empty'; empty.textContent = availableSymbols.length ? 'Không tìm thấy mã phù hợp.' : 'Chưa có mã nào.'; list.append(empty); return;
  }
  filtered.forEach((symbol) => {
    const item = document.createElement('li');
    const button = document.createElement('button');
    button.className = `watchlist-item${symbol === currentSymbol ? ' selected' : ''}`;
    button.type = 'button';
    button.innerHTML = `<strong>${escapeHtml(symbol)}</strong><span>${symbol === currentSymbol ? 'Đang xem' : 'Xem chi tiết'} <span aria-hidden="true">→</span></span>`;
    button.addEventListener('click', () => loadSymbol(symbol));
    item.append(button); list.append(item);
  });
}

async function loadSymbol(symbol) {
  currentSymbol = String(symbol).trim().toUpperCase();
  if (isDashboard()) {
    const heading = byId('dashboard-symbol'); if (heading) heading.textContent = currentSymbol || '—';
    renderWatchlist(byId('watchlist-filter')?.value || '');
  } else {
    const heading = byId('current-symbol'); if (heading) heading.textContent = currentSymbol || 'Mã cổ phiếu';
    const dashboardLink = byId('dashboard-link'); if (dashboardLink) dashboardLink.href = `/?symbol=${encodeURIComponent(currentSymbol)}`;
  }
  document.body.classList.add('loading');
  setStatus('ohlcv-status', `Đang tải dữ liệu ${currentSymbol}…`);
  try {
    const payload = await api(`/api/stocks/${encodeURIComponent(currentSymbol)}?limit=90`);
    allRows = Array.isArray(payload.data) ? payload.data : [];
    tableExpanded = false;
    if (isDashboard()) {
      renderDashboardSummary(allRows);
      renderDashboardChart(allRows.slice(-selectedPeriod));
    } else {
      renderDetailSummary(allRows);
      renderDetailChart(allRows.slice(-selectedPeriod));
    }
    renderTable();
    setStatus('ohlcv-status', allRows.length ? `Đã tải ${allRows.length} phiên OHLCV.` : 'Mã này chưa có dữ liệu OHLCV.', allRows.length ? 'success' : 'error');
    if (isDashboard()) setStatus('dashboard-data-status', allRows.length ? `Dữ liệu mới nhất: ${formatDate(allRows[allRows.length - 1].Date)}` : 'Chưa có dữ liệu', '');
  } catch (error) {
    allRows = [];
    if (isDashboard()) { renderDashboardSummary([]); renderDashboardChart([]); }
    else { renderDetailSummary([]); renderDetailChart([]); }
    renderTable();
    setStatus('ohlcv-status', error.status === 404 ? `Chưa có dữ liệu cho mã ${currentSymbol}.` : 'Không thể tải dữ liệu. Vui lòng thử lại.', 'error');
    if (isDashboard()) setStatus('dashboard-data-status', 'Không tải được dữ liệu', '');
  } finally { document.body.classList.remove('loading'); }
}

function clearDashboardData() { allRows = []; renderDashboardSummary([]); renderDashboardChart([]); renderTable(); setStatus('ohlcv-status', 'Chọn một mã để tải dữ liệu.', ''); }

function renderDashboardSummary(rows) {
  const latest = rows[rows.length - 1]; const previous = rows.length > 1 ? rows[rows.length - 2] : null;
  const setText = (id, value) => { const element = byId(id); if (element) element.textContent = value; };
  setText('dashboard-symbol', currentSymbol || '—');
  setText('dashboard-latest-date', latest ? `Dữ liệu mới nhất: ${formatDate(latest.Date)}` : 'Dữ liệu mới nhất: —');
  setText('dashboard-close', latest ? formatPrice(latest.Close) : '—');
  setText('dashboard-high-low', latest ? `${formatPrice(latest.High)} / ${formatPrice(latest.Low)}` : '—');
  setText('dashboard-volume', latest ? formatVolume(latest.Volume) : '—');
  setText('dashboard-date-range', rows.length ? `${formatDate(rows[0].Date)} – ${formatDate(latest.Date)}` : '—');
  setText('dashboard-session-count', rows.length ? `${rows.length} phiên` : 'Chưa có dữ liệu');
  const change = byId('dashboard-change'); const changePercent = byId('dashboard-change-percent');
  if (!change) return;
  change.className = 'neutral';
  if (!latest || !previous) { change.textContent = '—'; if (changePercent) changePercent.textContent = 'Chưa đủ dữ liệu'; return; }
  const difference = Number(latest.Close) - Number(previous.Close); const percent = Number(previous.Close) ? (difference / Number(previous.Close)) * 100 : null; const sign = difference > 0 ? '+' : '';
  change.className = difference > 0 ? 'positive' : difference < 0 ? 'negative' : 'neutral';
  change.textContent = `${sign}${formatPrice(difference)}`;
  if (changePercent) changePercent.textContent = percent === null ? 'Chưa tính được %' : `${sign}${formatPrice(percent)}% so với phiên trước`;
}

function renderDetailSummary(rows) {
  const latest = rows[rows.length - 1]; const previous = rows.length > 1 ? rows[rows.length - 2] : null;
  const setText = (id, value) => { const element = byId(id); if (element) element.textContent = value; };
  setText('summary-count', rows.length ? `${rows.length} phiên` : '—'); setText('summary-range', rows.length ? `${formatDate(rows[0].Date)} – ${formatDate(latest.Date)}` : '—'); setText('summary-latest-date', latest ? formatDate(latest.Date) : '—'); setText('summary-close', latest ? `${formatPrice(latest.Close)} nghìn VNĐ` : '—');
  const change = byId('summary-change'); if (!change) return; change.className = 'neutral';
  if (!latest || !previous) { change.textContent = 'Chưa đủ dữ liệu'; return; }
  const difference = Number(latest.Close) - Number(previous.Close); const percent = Number(previous.Close) ? (difference / Number(previous.Close)) * 100 : null; const sign = difference > 0 ? '+' : '';
  change.className = difference > 0 ? 'positive' : difference < 0 ? 'negative' : 'neutral'; change.textContent = `${sign}${formatPrice(difference)} (${percent === null ? '—' : `${sign}${formatPrice(percent)}%`})`;
}

function renderTable() {
  const body = byId('ohlcv-table'); if (!body) return; body.replaceChildren();
  const rows = allRows.slice().reverse(); const visibleRows = tableExpanded ? rows : rows.slice(0, 20);
  visibleRows.forEach((row) => { const tr = document.createElement('tr'); [formatDate(row.Date), formatPrice(row.Open), formatPrice(row.High), formatPrice(row.Low), formatPrice(row.Close), formatVolume(row.Volume)].forEach((value, index) => { const cell = document.createElement('td'); cell.textContent = value; if (index > 0) cell.className = 'number-cell'; tr.append(cell); }); body.append(tr); });
  const toggle = byId('toggle-table'); if (toggle) { toggle.hidden = rows.length <= 20; toggle.textContent = tableExpanded ? 'Thu gọn' : `Xem thêm (${rows.length - 20})`; }
}

function renderDashboardChart(rows) {
  const chartElement = byId('chart'); if (!chartElement) return;
  if (!rows.length) { disposeDashboardChart(); chartElement.innerHTML = '<div class="chart-empty">Chưa có dữ liệu OHLCV để hiển thị.</div>'; return; }
  if (!window.echarts) { chartElement.innerHTML = '<div class="chart-empty">Không tải được thư viện biểu đồ. Bảng dữ liệu bên dưới vẫn khả dụng.</div>'; return; }
  if (!dashboardChart) dashboardChart = window.echarts.init(chartElement, null, { renderer: 'canvas' });
  const dates = rows.map((row) => formatDate(row.Date));
  dashboardChart.setOption({
    animation: false,
    grid: { left: 58, right: 20, top: 24, bottom: 44 },
    tooltip: { trigger: 'axis', axisPointer: { type: 'line' }, confine: true, formatter: (params) => {
      const item = params[0]; const row = rows[item.dataIndex];
      return `<strong>${escapeHtml(formatDate(row.Date))}</strong><br>Open: ${formatPrice(row.Open)}<br>High: ${formatPrice(row.High)}<br>Low: ${formatPrice(row.Low)}<br>Close: ${formatPrice(row.Close)}<br>Volume: ${formatVolume(row.Volume)}`;
    }},
    xAxis: { type: 'category', boundaryGap: false, data: dates, axisLabel: { color: '#66768a', hideOverlap: true }, axisLine: { lineStyle: { color: '#cbd5e1' } } },
    yAxis: { type: 'value', name: 'Nghìn VNĐ', nameTextStyle: { color: '#66768a' }, axisLabel: { color: '#66768a', formatter: (value) => formatPrice(value) }, splitLine: { lineStyle: { color: '#e7edf4' } } },
    series: [{ name: 'Close', type: 'line', data: rows.map((row) => Number(row.Close)), smooth: false, symbol: rows.length <= 2 ? 'circle' : 'none', symbolSize: 7, lineStyle: { color: '#1769aa', width: 2 }, itemStyle: { color: '#1769aa' }, areaStyle: { color: 'rgba(23, 105, 170, .08)' } }]
  }, true);
  if (!dashboardChartObserver && window.ResizeObserver) { dashboardChartObserver = new ResizeObserver(() => dashboardChart?.resize()); dashboardChartObserver.observe(chartElement); }
  else if (!dashboardChartObserver) window.addEventListener('resize', () => dashboardChart?.resize());
}

function disposeDashboardChart() { if (dashboardChartObserver) { dashboardChartObserver.disconnect(); dashboardChartObserver = null; } if (dashboardChart) { dashboardChart.dispose(); dashboardChart = null; } }

function renderDetailChart(rows) {
  const chart = byId('chart'); if (!chart) return; if (!rows.length) { chart.innerHTML = '<div class="chart-empty">Chưa có dữ liệu OHLCV để hiển thị.</div>'; return; }
  const values = rows.map((row) => Number(row.Close)); const minValue = Math.min(...values); const maxValue = Math.max(...values); const padding = (maxValue - minValue || Math.max(maxValue * .02, 1)) * .12; const min = Math.max(0, minValue - padding); const range = maxValue + padding - min || 1; const width = 800; const height = 320; const left = 62; const top = 24; const plotWidth = width - left - 18; const plotHeight = height - top - 48; const x = (index) => left + index / Math.max(rows.length - 1, 1) * plotWidth; const y = (value) => top + (1 - (value - min) / range) * plotHeight; const points = values.map((value, index) => `${x(index)},${y(value)}`).join(' ');
  const grid = [0, 1, 2, 3, 4].map((step) => { const value = min + range * step / 4; const lineY = y(value); return `<line class="chart-grid" x1="${left}" y1="${lineY}" x2="${width - 18}" y2="${lineY}"/><text class="chart-axis-label" x="${left - 8}" y="${lineY + 4}" text-anchor="end">${formatPrice(value)}</text>`; }).join('');
  const labels = [...new Set([0, Math.floor((rows.length - 1) / 2), rows.length - 1])].map((index) => `<text class="chart-axis-label" x="${x(index)}" y="${height - 16}" text-anchor="middle">${formatDate(rows[index].Date)}</text>`).join('');
  chart.innerHTML = `<svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-label="Biểu đồ giá đóng cửa của ${escapeHtml(currentSymbol)}">${grid}${labels}<polyline class="chart-line" points="${points}"/></svg>`;
}

async function loadMarketStatus() { try { const status = await api('/api/market-status'); const element = byId('market-status'); if (element) { element.textContent = `Thị trường ${status.is_open ? 'mở' : 'đóng'}`; element.classList.toggle('open', status.is_open); } } catch (_) { const element = byId('market-status'); if (element) element.textContent = 'Không rõ trạng thái'; } }
function setStatus(id, message, kind = '') { const element = byId(id); if (element) { element.textContent = message; element.className = `status ${kind}`; } }
function formatDate(value) { return String(value || '').slice(0, 10) || '—'; }
function formatPrice(value) { return numberFormat.format(Number(value)); }
function formatVolume(value) { return integerFormat.format(Number(value)); }
function escapeHtml(value) { return String(value).replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character])); }
