function goToStep(step) {
    const totalSteps = 4;
    if (step < 1 || step > totalSteps) return;

    document.querySelectorAll('.form-step').forEach(el => el.classList.remove('active'));
    document.querySelector(`.form-step[data-step="${step}"]`).classList.add('active');

    document.querySelectorAll('.step-dot').forEach(el => {
        const s = parseInt(el.dataset.step, 10);
        el.classList.remove('active', 'done');
        if (s === step) el.classList.add('active');
        if (s < step) el.classList.add('done');
    });

    updateStepLabel(step);
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateStepLabel(step) {
    const labels = ['', 'Type de bien', 'Localisation', 'Caractéristiques', 'Résultat'];
    const el = document.getElementById('stepLabel');
    if (el) el.textContent = `Étape ${step}/3 — ${labels[step] || ''}`;
}

function formatEuros(value) {
    return `${Math.round(value).toLocaleString('fr-FR')} €`;
}

// Stocke les données de la dernière estimation
let lastEstimationData = null;
let lastEstimationResult = null;

async function submitEstimation() {
    const data = {
        surface_m2: parseFloat(document.getElementById('surface_m2').value),
        nb_pieces: parseInt(document.getElementById('nb_pieces').value, 10),
        type_bien: document.getElementById('type_bien').value,
        ville: document.getElementById('ville').value.trim(),
        code_postal: document.getElementById('code_postal').value.trim(),
        etage: parseInt(document.getElementById('etage').value, 10) || 0,
        annee_construction: parseInt(document.getElementById('annee_construction').value, 10) || 2000,
        etat_general: parseInt(document.getElementById('etat_general').value, 10) || 3,
        has_garage: document.getElementById('has_garage').checked,
        has_jardin: document.getElementById('has_jardin').checked,
        has_piscine: document.getElementById('has_piscine').checked
    };

    if (!data.type_bien || !data.ville || !data.code_postal || !data.surface_m2 || !data.nb_pieces) {
        showEstimError('Veuillez remplir tous les champs obligatoires (type, ville, code postal, surface, pièces).');
        return;
    }

    lastEstimationData = data;

    goToStep(4);
    document.querySelector('#resultContent').innerHTML = `
        <div class="result-loading">
            <div class="spinner"></div>
            <p>Analyse des données du marché...</p>
            <small>${data.ville} · ${data.surface_m2} m² · ${data.nb_pieces} pièces</small>
        </div>
    `;

    try {
        const response = await fetch(`${API_URL}/estimation/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (!response.ok) throw new Error(result.detail || 'Erreur API');

        lastEstimationResult = result;
        displayResult(data, result);

    } catch (error) {
        document.querySelector('#resultContent').innerHTML = `
            <div class="result-error">
                <div class="error-icon">⚠️</div>
                <p class="error-title">Estimation impossible</p>
                <p class="error-msg">${error.message}</p>
                <button class="btn btn-primary" onclick="goToStep(3)">Réessayer</button>
            </div>
        `;
    }
}

function displayResult(data, result) {
    const confidence = Math.round(result.score_confiance * 100);
    const confidenceColor = confidence >= 80 ? '#059669' : confidence >= 60 ? '#d97706' : '#dc2626';
    const typeLabel = { maison: 'Maison', appartement: 'Appartement', commerce: 'Local commercial' };

    document.querySelector('#resultContent').innerHTML = `
        <div class="result-hero">
            <div class="result-type-badge">${typeLabel[data.type_bien] || data.type_bien}</div>
            <div class="result-location">📍 ${data.ville}, ${data.code_postal}</div>
            <div class="result-price">${formatEuros(result.prix_estime)}</div>
            <div class="result-range">Fourchette : ${formatEuros(result.prix_min)} – ${formatEuros(result.prix_max)}</div>
        </div>

        <div class="result-details">
            <div class="detail-card">
                <div class="detail-icon">📐</div>
                <div class="detail-value">${formatEuros(result.prix_m2_zone)}</div>
                <div class="detail-label">Prix au m²</div>
            </div>
            <div class="detail-card">
                <div class="detail-icon">🏠</div>
                <div class="detail-value">${data.surface_m2} m²</div>
                <div class="detail-label">Surface</div>
            </div>
            <div class="detail-card">
                <div class="detail-icon">🚪</div>
                <div class="detail-value">${data.nb_pieces}</div>
                <div class="detail-label">Pièces</div>
            </div>
        </div>

        <div class="confidence-block">
            <div class="confidence-header">
                <span>Indice de confiance</span>
                <span style="font-weight:700; color:${confidenceColor};">${confidence}%</span>
            </div>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width:${confidence}%; background:${confidenceColor};"></div>
            </div>
        </div>

        <div class="result-cta">
            <button class="cta-btn primary" onclick="mettreEnVente()">
                🏷️ Mettre en vente
            </button>
            <button class="cta-btn secondary" onclick="contactAgent()">
                📞 Être contacté par un agent
            </button>
            <button class="cta-btn ghost" onclick="goToStep(1)">
                🔄 Nouvelle estimation
            </button>
        </div>
    `;
}

function showEstimError(msg) {
    // Afficher une erreur inline dans l'étape active
    let el = document.querySelector('.form-step.active .form-error');
    if (!el) {
        el = document.createElement('p');
        el.className = 'form-error';
        document.querySelector('.form-step.active .btn-group').insertAdjacentElement('beforebegin', el);
    }
    el.textContent = msg;
    setTimeout(() => el.remove(), 4000);
}

function contactAgent() {
    // Toast à la place de l'alert
    showToast('✅ Un agent Ymmo vous contactera dans les plus brefs délais !');
}

function mettreEnVente() {
    if (!localStorage.getItem('ymmo_token')) {
        showToast('Connectez-vous d\'abord pour mettre votre bien en vente.', 'warn');
        setTimeout(() => window.location.href = 'login.html', 1500);
        return;
    }

    // Sauvegarder les données pour pré-remplir le dashboard
    const prefill = {
        ...lastEstimationData,
        prix_estime: lastEstimationResult?.prix_estime
    };
    sessionStorage.setItem('ymmo_prefill', JSON.stringify(prefill));
    window.location.href = 'dashboard.html?action=add';
}

function showToast(message, type = 'success') {
    let toast = document.getElementById('estim-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'estim-toast';
        toast.style.cssText = `
            position:fixed; bottom:24px; right:24px;
            background:#111827; color:white;
            padding:12px 20px; border-radius:10px;
            font-size:14px; font-weight:500;
            box-shadow:0 4px 16px rgba(0,0,0,.2);
            opacity:0; transform:translateY(8px);
            transition:all .3s; z-index:9999;
        `;
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.style.background = type === 'warn' ? '#92400e' : '#111827';
    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    });
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(8px)';
    }, 3500);
}
