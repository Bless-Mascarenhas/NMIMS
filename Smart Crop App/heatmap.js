/* heatmap.js - enhanced dev frontend
   - Calls backend endpoints: /api/heatmap-data, /api/alerts, /api/region-details, /api/trend-data
   - Renders heatmap grid, recent alerts, region details and monthly trend chart
*/

const API_BASE = '/api';

let heatmapData = [];
let trendChart = null;

async function loadHeatmap() {
    const container = document.getElementById('heatmapGrid');
    if (!container) return;

    const state = document.getElementById('stateFilter')?.value || 'all';
    const district = document.getElementById('districtFilter')?.value || 'all';
    const crop = document.getElementById('cropFilter')?.value || 'all';
    const season = document.getElementById('seasonFilter')?.value || '';

    const params = new URLSearchParams({ state, district, crop, season });

    try {
        const res = await fetch(`${API_BASE}/heatmap-data?${params}`);
        if (!res.ok) throw new Error('Failed to fetch heatmap-data');
        const payload = await res.json();
        heatmapData = payload.data || [];

        if (heatmapData.length === 0) {
            container.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:3rem;color:#888;">No heatmap data available for selected filters</div>`;
            return;
        }

        container.innerHTML = heatmapData.map(zone => {
            const cls = zone.risk_level ? zone.risk_level.toLowerCase() : 'low';
            return `
                <div class="heatmap-zone ${cls}" data-state="${zone.state}" data-district="${zone.district}" data-crop="${zone.crop}">
                    <div class="zone-header">
                        <div class="zone-location">
                            <h3>${zone.district}</h3>
                            <p>${zone.state} • ${zone.crop}</p>
                        </div>
                        <div class="risk-badge">${zone.risk_level}</div>
                    </div>
                    <div class="zone-info">
                        <p><strong>Risk Score:</strong> <span>${zone.risk_score}</span></p>
                        <p><strong>Humidity:</strong> <span>${zone.humidity}%</span></p>
                        <p><strong>Temp:</strong> <span>${zone.temperature}°C</span></p>
                        <p><strong>Diseases:</strong> <span>${zone.diseases.length}</span></p>
                    </div>
                </div>
            `;
        }).join('');

        updateHeaderStats();
    } catch (err) {
        console.error('loadHeatmap error', err);
        container.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:3rem;color:#f44336;">Failed to load heatmap data. Check backend.</div>`;
    }
}

async function loadAlerts(limit = 4) {
    const container = document.getElementById('alertsContainer');
    if (!container) return;
    try {
        const res = await fetch(`${API_BASE}/alerts?limit=${limit}`);
        if (!res.ok) throw new Error('Failed to fetch alerts');
        const payload = await res.json();
        const alerts = payload.alerts || [];

        if (alerts.length === 0) {
            container.innerHTML = `<p style="grid-column:1/-1;text-align:center;color:#888;">No recent alerts</p>`;
            return;
        }

        container.innerHTML = alerts.map(a => `
            <div class="alert-card ${a.severity && a.severity.toLowerCase() === 'high' ? 'high' : ''}">
                <div class="alert-header">
                    <span class="alert-title">⚠️ ${a.disease} - ${a.crop}</span>
                    <span class="alert-date">${new Date(a.date).toLocaleString()}</span>
                </div>
                <div class="alert-body">
                    <p><strong>Location:</strong> ${a.district}, ${a.state}</p>
                    <p><strong>Severity:</strong> ${a.severity}</p>
                    <p><strong>Affected Area:</strong> ${a.affected_area} acres</p>
                    <p class="alert-message">${a.message}</p>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error('loadAlerts error', err);
        container.innerHTML = `<p style="grid-column:1/-1;text-align:center;color:#f44336;">Failed to load alerts</p>`;
    }
}

async function loadTrendChart() {
    try {
        const state = document.getElementById('stateFilter')?.value || 'All';
        const crop = document.getElementById('cropFilter')?.value || 'Rice';
        const res = await fetch(`${API_BASE}/trend-data?state=${encodeURIComponent(state)}&crop=${encodeURIComponent(crop)}`);
        if (!res.ok) throw new Error('Failed to fetch trend data');
        const payload = await res.json();

        const ctx = document.getElementById('trendChart');
        if (!ctx) return;

        const labels = payload.labels || [];
        const data = payload.data || [];

        if (trendChart) {
            trendChart.destroy();
        }

        trendChart = new Chart(ctx, {
            type: 'line',
            data: { labels, datasets: [{ label: `Disease Risk - ${payload.crop || crop}`, data, borderColor: '#ff5722', backgroundColor: 'rgba(255,87,34,0.1)', tension: 0.3 }] },
            options: { responsive: true, maintainAspectRatio: false }
        });
    } catch (err) {
        console.error('loadTrendChart error', err);
    }
}

function applyFilters() {
    loadHeatmap();
    loadAlerts();
    loadTrendChart();
}

function updateHeaderStats() {
    const activeOutbreaks = heatmapData.filter(z => (z.diseases || []).length > 0).length;
    const highRiskAreas = heatmapData.filter(z => (z.risk_level || '').toLowerCase() === 'high').length;
    const aEl = document.getElementById('activeOutbreaks');
    const hEl = document.getElementById('highRiskCount');
    if (aEl) aEl.textContent = String(activeOutbreaks);
    if (hEl) hEl.textContent = String(highRiskAreas);
}

// When clicking a heatmap zone, fetch region details from backend
document.addEventListener('click', async function(e) {
    const zoneEl = e.target.closest('.heatmap-zone');
    if (!zoneEl) return;
    const state = zoneEl.getAttribute('data-state');
    const district = zoneEl.getAttribute('data-district');
    const crop = zoneEl.getAttribute('data-crop');

    try {
        const res = await fetch(`${API_BASE}/region-details?state=${encodeURIComponent(state)}&district=${encodeURIComponent(district)}&crop=${encodeURIComponent(crop)}`);
        if (!res.ok) throw new Error('Failed to fetch region details');
        const details = await res.json();

        const regionDetails = document.getElementById('regionDetails');
        if (!regionDetails) return;

        regionDetails.innerHTML = `
            <div class="detail-card">
                <h4>📍 ${details.district}, ${details.state}</h4>
                <p>Crop: <strong>${details.crop}</strong> • Season: ${details.season}</p>
            </div>
            <div class="detail-card">
                <h4>⚠️ Risk Assessment</h4>
                <p>Risk Level: <span class="risk-indicator ${details.risk_level.toLowerCase()}">${details.risk_level}</span></p>
                <p>Risk Score: <strong>${details.risk_score}/100</strong></p>
                <p>Last Updated: ${new Date(details.last_updated).toLocaleString()}</p>
            </div>
            <div class="detail-card">
                <h4>🦠 Active Diseases</h4>
                <ul>${(details.diseases || []).map(d => `<li>${d}</li>`).join('')}</ul>
            </div>
            <div class="detail-card">
                <h4>💡 Recommendations</h4>
                <ul>${(details.recommendations || []).map(r => `<li>${r}</li>`).join('')}</ul>
            </div>
        `;
    } catch (err) {
        console.error('Error loading region details', err);
    }
});

// Modal handling
function openReportModal() { const m = document.getElementById('reportModal'); if (m) m.style.display = 'block'; }
function closeReportModal() { const m = document.getElementById('reportModal'); if (m) m.style.display = 'none'; const f = document.getElementById('reportForm'); if (f) f.reset(); }
window.addEventListener('click', function(e) { const modal = document.getElementById('reportModal'); if (modal && e.target === modal) closeReportModal(); });

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    applyFilters();
});

console.log('heatmap.js initialized - enhanced');