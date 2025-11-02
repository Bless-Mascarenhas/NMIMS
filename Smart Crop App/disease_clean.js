// disease_clean.js - clean implementation used by disease.html
window.DISEASE_JS_LOADED = true;

const DISEASES = [
  {
    id: 'leaf_blight',
    name: 'Leaf Blight',
    summary: 'Fungal disease causing brown lesions and rapid leaf necrosis.',
    symptoms: ['Brown spots', 'Yellowing', 'Lesion expansion', 'Leaf curling'],
    advice: ['Apply recommended fungicide', 'Remove heavily infected plants', 'Improve aeration']
  },
  {
    id: 'rust',
    name: 'Rust',
    summary: 'Orange-brown pustules on leaf undersides that reduce photosynthesis.',
    symptoms: ['Orange pustules', 'Yellow specks', 'Reduced vigor'],
    advice: ['Remove infected debris', 'Rotate crops', 'Use resistant varieties']
  },
  {
    id: 'yellowing',
    name: 'Yellowing / Chlorosis',
    summary: 'Nutrient deficiency or water stress leading to yellow leaves.',
    symptoms: ['Yellow leaves', 'Stunted growth', 'Interveinal chlorosis'],
    advice: ['Test and correct soil pH', 'Apply balanced fertilizer', 'Check irrigation']
  }
];

document.addEventListener('DOMContentLoaded', () => {
  try {
    const grid = document.getElementById('diseaseGrid');
    const details = document.getElementById('diseaseDetails');
    const symptomContainer = document.getElementById('symptomCheckboxes');
    const resultsEl = document.getElementById('results');

    function escapeHtml(s) {
      return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }

    function initGrid() {
      if (!grid) return;
      grid.innerHTML = '';
      DISEASES.forEach(d => {
        const card = document.createElement('div');
        card.className = 'disease-card';
        card.textContent = d.name;
        card.onclick = () => showDetails(d);
        grid.appendChild(card);
      });
    }

    function showDetails(disease) {
      if (!details) return;
      document.querySelectorAll('.disease-card').forEach(c => c.classList.remove('active'));
      const active = Array.from(document.querySelectorAll('.disease-card')).find(n => n.textContent === disease.name);
      if (active) active.classList.add('active');
      details.innerHTML = `
        <h3>${escapeHtml(disease.name)}</h3>
        <p style="color:#718096">${escapeHtml(disease.summary)}</p>
        <h4 style="margin-top:12px">Common symptoms</h4>
        <ul class="symptom-list">
          ${disease.symptoms.map(s => `<li>${escapeHtml(s)}</li>`).join('')}
        </ul>
        <h4 style="margin-top:12px">Recommendations</h4>
        <ul>
          ${disease.advice.map(a => `<li>${escapeHtml(a)}</li>`).join('')}
        </ul>
      `;
    }

    function initSymptomCheckboxes() {
      if (!symptomContainer) return;
      const set = new Set();
      DISEASES.forEach(d => d.symptoms.forEach(s => set.add(s)));
      const arr = Array.from(set).sort();
      symptomContainer.innerHTML = '';
      arr.forEach((symptom, idx) => {
        const div = document.createElement('div');
        div.className = 'symptom-checkbox';
        const id = 'symp_' + idx;
        div.innerHTML = `<input type="checkbox" id="${id}" value="${escapeHtml(symptom)}"><label for="${id}">${escapeHtml(symptom)}</label>`;
        symptomContainer.appendChild(div);
      });
    }

    window.diagnose = function() {
      if (!resultsEl) return;
      const checked = Array.from(document.querySelectorAll('#symptomCheckboxes input:checked')).map(i => i.value);
      if (!checked.length) {
        resultsEl.innerHTML = `<div class="no-results"><div class="emoji">⚠</div>Please select at least one symptom to diagnose</div>`;
        return;
      }

      const matches = [];
      DISEASES.forEach(d => {
        const matched = checked.filter(s => d.symptoms.includes(s));
        if (matched.length) {
          const pct = Math.round((matched.length / checked.length) * 100);
          matches.push({ name: d.name, pct, matched, other: d.symptoms.filter(s => !matched.includes(s)) });
        }
      });
      matches.sort((a,b) => b.pct - a.pct);

      if (!matches.length) {
        resultsEl.innerHTML = `<div class="no-results"><div class="emoji">🤔</div>No matching diseases found. Please consult an expert.</div>`;
        return;
      }

      resultsEl.innerHTML = matches.map(m => `
        <div class="result-item">
          <h4>${escapeHtml(m.name)}</h4>
          <div class="match-percentage">${m.pct}% Match</div>
          <p style="color:#718096;margin-top:8px">Matched: ${m.matched.map(s => escapeHtml(s)).join(', ')}</p>
          ${m.other.length ? `<p style="color:#718096;margin-top:6px">Other symptoms: ${m.other.map(s => escapeHtml(s)).join(', ')}</p>` : ''}
        </div>
      `).join('');
    };

    async function checkBackend() {
      const statusEl = document.getElementById('diseaseStatus');
      if (!statusEl) return;
      try {
        const r = await fetch('/api/alerts?limit=1');
        if (r.ok) {
          statusEl.style.display = 'block'; statusEl.style.color = '#0b6b57'; statusEl.textContent = 'Backend: reachable';
        } else {
          statusEl.style.display = 'block'; statusEl.style.color = '#b45309'; statusEl.textContent = 'Backend responded ' + r.status;
        }
      } catch (err) {
        statusEl.style.display = 'block'; statusEl.style.color = '#c53030'; statusEl.textContent = 'Backend unreachable — using fallback';
      }
    }

    initGrid();
    initSymptomCheckboxes();
    if (DISEASES.length) showDetails(DISEASES[0]);
    checkBackend();
  } catch (err) {
    console.error('disease_clean.js init error', err);
    const statusEl = document.getElementById('diseaseStatus');
    if (statusEl) { statusEl.style.display='block'; statusEl.style.color='#c53030'; statusEl.textContent = 'Disease UI error: ' + (err && err.message ? err.message : String(err)); }
  }
});
