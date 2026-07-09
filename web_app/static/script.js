// ── Tab System ───────────────────────────────────────
function showTab(name) {
    document.querySelectorAll('.tab').forEach(t => t.classList.add('hidden'));
    document.querySelectorAll('.navtab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + name).classList.remove('hidden');
    document.getElementById('navtab-' + name).classList.add('active');
    if (name === 'risk')       loadRisk();
    if (name === 'timeseries') loadTimeSeries();
}

// ── Dashboard: load stats + images ──────────────────
fetch('/api/stats').then(r => r.json()).then(d => {
    document.getElementById('s-uplift').textContent = d.max_uplift_cm   ? d.max_uplift_cm.toFixed(1)   : '--';
    document.getElementById('s-subs').textContent   = d.max_subsidence_cm ? d.max_subsidence_cm.toFixed(1) : '--';
    document.getElementById('s-mean').textContent   = d.mean_displacement_cm ? d.mean_displacement_cm.toFixed(2) : '--';
    document.getElementById('s-px').textContent     = d.valid_pixels     ? d.valid_pixels.toLocaleString() : '--';
});
fetch('/api/displacement-map').then(r=>r.json()).then(d=>{
    document.getElementById('disp-map').src = 'data:image/png;base64,' + d.image;
});
fetch('/api/historical-chart').then(r=>r.json()).then(d=>{
    document.getElementById('hist-chart').src = 'data:image/png;base64,' + d.image;
});

// ── Risk Monitor ─────────────────────────────────────
function loadRisk() {
    document.getElementById('risk-ts').textContent = 'Loading...';
    fetch('/api/risk').then(r => r.json()).then(applyRisk);
}

function applyRisk(d) {
    const orb = document.getElementById('risk-orb');
    orb.style.borderColor = d.color;
    orb.style.background  = d.color + '18';
    orb.style.boxShadow   = `0 0 28px ${d.color}44`;
    document.getElementById('risk-lbl').textContent   = d.level;
    document.getElementById('risk-lbl').style.color   = d.color;
    document.getElementById('risk-score').textContent = `${d.score}/100`;
    document.getElementById('kv-vel').textContent  = `${d.velocity} cm/acq`;
    document.getElementById('kv-mag').textContent  = `M ${d.magnitude_estimate}`;
    document.getElementById('kv-pop').textContent  = d.affected_population;
    const msgBox = document.getElementById('risk-msg');
    msgBox.textContent           = d.message;
    msgBox.style.borderLeftColor = d.color;
    document.getElementById('risk-ts').textContent = 'Updated: ' + new Date().toLocaleTimeString();

    // Param cards
    document.getElementById('p-vel').textContent  = d.velocity;
    document.getElementById('p-score').textContent = d.score;
    document.getElementById('pf-vel').style.width   = Math.min(d.velocity * 20, 100) + '%';
    document.getElementById('pf-score').style.width = d.score + '%';
    if (d.std_values && d.std_values.length) {
        const avg = d.std_values.reduce((a,b)=>a+b,0) / d.std_values.length;
        document.getElementById('p-std').textContent = avg.toFixed(2);
        document.getElementById('pf-std').style.width = Math.min(avg * 10, 100) + '%';
    }
}

// ── Time Series ──────────────────────────────────────
function loadTimeSeries() {
    const body = document.getElementById('ts-body');
    body.innerHTML = '<div class="loading">⏳ Analysing all interferograms...</div>';
    fetch('/api/time-series').then(r => r.json()).then(data => {
        if (!data || !data.length) {
            body.innerHTML = '<div class="loading">No data found.</div>'; return;
        }
        const valid = data.filter(d => !d.error);
        let html = '<div class="ts-list">';
        data.forEach((item, i) => {
            if (item.error) {
                html += `<div class="ts-item">
                    <div class="ts-num">${i+1}</div>
                    <div><div class="ts-file">${item.file}</div>
                    <div class="ts-dates" style="color:#ff5252">⚠ ${item.error}</div></div>
                    <div></div><div></div><div></div></div>`;
            } else {
                html += `<div class="ts-item">
                    <div class="ts-num">${i+1}</div>
                    <div><div class="ts-file">📁 ${item.file}</div>
                    <div class="ts-dates">📅 ${item.date1} → ${item.date2}</div></div>
                    <div class="ts-stat"><div class="ts-stat-val c-green">+${item.max_uplift.toFixed(1)}</div><div class="ts-stat-lbl">Max Uplift (cm)</div></div>
                    <div class="ts-stat"><div class="ts-stat-val c-red">${item.max_subsidence.toFixed(1)}</div><div class="ts-stat-lbl">Max Subsidence (cm)</div></div>
                    <div class="ts-stat"><div class="ts-stat-val c-blue">${item.valid_pixels.toLocaleString()}</div><div class="ts-stat-lbl">Valid Pixels</div></div>
                </div>`;
            }
        });
        html += '</div>';

        if (valid.length >= 2) {
            const vel = Math.abs(valid[valid.length-1].mean_disp - valid[0].mean_disp) / valid.length;
            const totalChange = Math.abs(valid[valid.length-1].mean_disp - valid[0].mean_disp).toFixed(2);
            const status = vel > 2
                ? `<span style="color:#ff1744">⚠️ Velocity exceeds normal baseline — elevated risk.</span>`
                : vel > 1
                ? `<span style="color:#ffd600">⚡ Velocity above baseline — monitoring recommended.</span>`
                : `<span style="color:#3ecf8e">✅ Velocity within normal baseline range.</span>`;
            html += `<div class="vel-box">
                <h3>📈 Velocity Analysis</h3>
                <p>Average deformation velocity across <strong>${valid.length} acquisitions</strong>:
                <strong style="color:#ffd600"> ${vel.toFixed(3)} cm/acquisition</strong><br>
                Total change: <strong style="color:#ff5252">${totalChange} cm</strong>
                between first and last acquisition.<br>${status}</p>
            </div>`;
        }
        body.innerHTML = html;
    });
}

// ── Alert System ─────────────────────────────────────
function triggerDemoAlert() {
    fetch('/api/trigger-alert', { method: 'POST' })
        .then(r => r.json())
        .then(showAlert);
}

function showAlert(d) {
    document.getElementById('alert-dialog-level').textContent = `⚠️ SEISMIC ALERT — ${d.level}`;
    document.getElementById('dlg-mag').textContent  = `M ${d.magnitude_estimate}`;
    document.getElementById('dlg-pop').textContent  = d.affected_population;
    document.getElementById('dlg-vel').textContent  = d.velocity;
    document.getElementById('dlg-summary').textContent =
        'Anomalous surface deformation detected along the Oldham Fault. ' +
        'Strain accumulation significantly above baseline threshold.';
    document.getElementById('dlg-full-msg').textContent = d.message;
    document.getElementById('alert-details').classList.add('hidden');
    document.querySelector('.see-more-btn').textContent = '▼ See Technical Details';
    document.getElementById('alert-overlay').classList.remove('hidden');
}

function dismissAlert() {
    document.getElementById('alert-overlay').classList.add('hidden');
}

function toggleDetails() {
    const det = document.getElementById('alert-details');
    const btn = document.querySelector('.see-more-btn');
    det.classList.toggle('hidden');
    btn.textContent = det.classList.contains('hidden')
        ? '▼ See Technical Details'
        : '▲ Hide Technical Details';
}

// ── Q&A ──────────────────────────────────────────────
function ask(q) {
    document.getElementById('chat-in').value = q;
    sendQ();
}

function sendQ() {
    const inp = document.getElementById('chat-in');
    const q   = inp.value.trim();
    if (!q) return;
    const box = document.getElementById('chatbox');

    const um = document.createElement('div');
    um.className = 'msg user'; um.textContent = q;
    box.appendChild(um);
    inp.value = '';
    box.scrollTop = box.scrollHeight;

    const bm = document.createElement('div');
    bm.className = 'msg bot'; bm.textContent = '...';
    box.appendChild(bm);

    fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q })
    }).then(r => r.json()).then(d => {
        bm.textContent = d.answer;
        box.scrollTop  = box.scrollHeight;
    });
}