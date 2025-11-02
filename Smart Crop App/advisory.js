// advisory.js - fetches market prices from backend and displays them
async function fetchMarket(commodity = '', state = '') {
    let url = '/api/market-prices';
    const params = [];
    if (commodity && commodity.trim()) params.push('commodity=' + encodeURIComponent(commodity.trim()));
    if (state && state !== 'all') params.push('state=' + encodeURIComponent(state));
    if (params.length) url += '?' + params.join('&');

    const resp = await fetch(url);
    const data = await resp.json();
    return data.prices || [];
}

function renderMarket(rows) {
    const tbody = document.getElementById('marketBody');
    const empty = document.getElementById('marketEmpty');
    tbody.innerHTML = '';
    if (!rows || rows.length === 0) {
        empty.classList.remove('hidden');
        return;
    }
    empty.classList.add('hidden');

    rows.forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${r.commodity}</td>
            <td>${r.mandi}</td>
            <td>${r.state}</td>
            <td>₹ ${r.price}</td>
            <td>${r.unit}</td>
            <td>${r.updated}</td>
        `;
        tbody.appendChild(tr);
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    const commodityInput = document.getElementById('commodityInput');
    const stateSelect = document.getElementById('stateSelect');
    const searchBtn = document.getElementById('searchMarket');
    const refreshBtn = document.getElementById('refreshMarket');

    async function load() {
        const rows = await fetchMarket(commodityInput.value, stateSelect.value);
        renderMarket(rows);
    }

    searchBtn.addEventListener('click', load);
    refreshBtn.addEventListener('click', load);
    commodityInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') load(); });

    // initial load
    await load();
});
