// schemes.js - client-side rendering and filtering for schemes page
const schemes = [
    {
        id: 'pmfby',
        title: 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
        category: 'insurance',
        region: 'National',
        description: 'Crop insurance to protect farmers against natural calamities, pests and diseases. Subsidized premium for small farmers.',
        link: 'https://pmfby.gov.in/'
    },
    {
        id: 'pmksy',
        title: 'Pradhan Mantri Krishi Sinchai Yojana (PMKSY)',
        category: 'irrigation',
        region: 'National',
        description: 'Irrigation and water-use efficiency projects for small and marginal farmers, micro-irrigation subsidies and projects support.',
        link: 'https://pmksy.gov.in/'
    },
    {
        id: 'kcc',
        title: 'Kisan Credit Card (KCC)',
        category: 'credit',
        region: 'National',
        description: 'Short-term crop loans and working capital support at subsidized interest rates; easy application through banks.',
        link: 'https://rbi.org.in/'
    },
    {
        id: 'shc',
        title: 'Soil Health Card (SHC)',
        category: 'soil',
        region: 'National',
        description: 'Free soil testing and personalised nutrient recommendations to improve fertility and yields.',
        link: 'https://soilhealth.dac.gov.in/'
    },
    {
        id: 'pmayu',
        title: 'State Irrigation Support - Punjab',
        category: 'irrigation',
        region: 'Punjab',
        description: 'Punjab state program supporting irrigation modernization and small canal repairs.',
        link: '#'
    },
    {
        id: 'up-insure',
        title: 'UP Crop Resilience Grant',
        category: 'insurance',
        region: 'Uttar Pradesh',
        description: 'State-level grant for flood-affected areas focusing on seed replacement and early recovery.',
        link: '#'
    },
    {
        id: 'maha-kcc',
        title: 'Maharashtra KCC Support',
        category: 'credit',
        region: 'Maharashtra',
        description: 'Additional interest subsidy for farmers holding Kisan Credit Cards in Maharashtra.',
        link: '#'
    }
];

function el(tag, cls, inner) {
    const d = document.createElement(tag);
    if (cls) d.className = cls;
    if (inner !== undefined) d.innerHTML = inner;
    return d;
}

function renderSchemes(list) {
    const container = document.getElementById('schemesList');
    container.innerHTML = '';
    if (!list || list.length === 0) {
        container.appendChild(el('div', 'muted', 'No schemes found matching your filters.'));
        return;
    }

    list.forEach(s => {
        const card = el('article', 'scheme-card');
        const h = el('h3', null, s.title);
        const p = el('p', null, s.description);
        const meta = el('div', 'scheme-meta', `${s.category.toUpperCase()} • ${s.region}`);
        const link = el('a', 'apply-link', 'Learn more');
        link.href = s.link || '#';
        link.target = '_blank';
        link.addEventListener('click', (ev) => {
            // allow external navigation but also open modal for in-app details
            // If link is '#', show modal instead
            if (!s.link || s.link === '#') {
                ev.preventDefault();
                openModal(s);
            }
        });

        card.appendChild(h);
        card.appendChild(p);
        card.appendChild(meta);
        card.appendChild(link);
        container.appendChild(card);
    });
}

function openModal(s) {
    const modal = document.getElementById('schemeModal');
    document.getElementById('modalTitle').textContent = s.title;
    document.getElementById('modalDescription').textContent = s.description;
    document.getElementById('modalRegion').textContent = `Region: ${s.region} • Category: ${s.category}`;
    const ml = document.getElementById('modalLink');
    ml.href = s.link || '#';
    if (!s.link || s.link === '#') ml.classList.add('hidden'); else ml.classList.remove('hidden');
    modal.classList.remove('hidden');
}

function closeModal() {
    const modal = document.getElementById('schemeModal');
    modal.classList.add('hidden');
}

function applyFilters() {
    const q = (document.getElementById('schemeSearch').value || '').toLowerCase().trim();
    const cat = document.getElementById('schemeCategory').value;
    const region = document.getElementById('schemeRegion').value;

    const filtered = schemes.filter(s => {
        const matchQ = !q || (s.title + ' ' + s.description + ' ' + s.category + ' ' + s.region).toLowerCase().includes(q);
        const matchC = (cat === 'all') || (s.category === cat);
        const matchR = (region === 'all') || (s.region === region);
        return matchQ && matchC && matchR;
    });

    renderSchemes(filtered);
}

// Wire controls
document.addEventListener('DOMContentLoaded', () => {
    renderSchemes(schemes);

    document.getElementById('schemeSearch').addEventListener('input', () => applyFilters());
    document.getElementById('schemeCategory').addEventListener('change', () => applyFilters());
    document.getElementById('schemeRegion').addEventListener('change', () => applyFilters());
    document.getElementById('clearFilters').addEventListener('click', () => {
        document.getElementById('schemeSearch').value = '';
        document.getElementById('schemeCategory').value = 'all';
        document.getElementById('schemeRegion').value = 'all';
        applyFilters();
    });

    document.getElementById('closeModal').addEventListener('click', closeModal);
    document.getElementById('schemeModal').addEventListener('click', (e) => { if (e.target.id === 'schemeModal') closeModal(); });
});
