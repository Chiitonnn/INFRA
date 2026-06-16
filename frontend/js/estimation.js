const API_URL = 'http://192.168.10.10/api';

function goToStep(step) {
    const totalSteps = 4;
    if (step < 1 || step > totalSteps) return;

    document.querySelectorAll('.form-step').forEach(el => el.classList.remove('active'));
    document.querySelector(`.form-step[data-step="${step}"]`).classList.add('active');

    document.querySelectorAll('.step-dot').forEach(el => {
        const s = parseInt(el.dataset.step);
        el.classList.remove('active', 'done');
        if (s === step) el.classList.add('active');
        else if (s < step) el.classList.add('done');
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function submitEstimation() {
    const data = {
        surface_m2: parseFloat(document.getElementById('surface_m2').value),
        nb_pieces: parseInt(document.getElementById('nb_pieces').value),
        type_bien: document.getElementById('type_bien').value,
        ville: document.getElementById('ville').value,
        code_postal: document.getElementById('code_postal').value,
        etage: parseInt(document.getElementById('etage').value) || 0,
        annee_construction: parseInt(document.getElementById('annee_construction').value) || 2000,
        etat_general: parseInt(document.getElementById('etat_general').value) || 3,
        has_garage: document.getElementById('has_garage').checked,
        has_jardin: document.getElementById('has_jardin').checked,
        has_piscine: document.getElementById('has_piscine').checked
    };

    // Validation
    if (!data.type_bien || !data.ville || !data.surface_m2 || !data.nb_pieces) {
        alert('Veuillez remplir tous les champs obligatoires.');
        return;
    }

    goToStep(4);
    document.querySelector('#resultContent').innerHTML = `
        <div class="result-box">
            <div style="font-size:40px; margin-bottom:16px;">⏳</div>
            <p>Calcul en cours...<br><small>L'IA analyse les données du marché</small></p>
        </div>
    `;

    try {
        const response = await fetch(`${API_URL}/estimation/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erreur API');
        }
        const result = await response.json();

        document.querySelector('#resultContent').innerHTML = `
            <div class="result-box">
                <div class="price">${result.prix_estime.toLocaleString('fr-FR')} €</div>
                <div class="range">${result.prix_min.toLocaleString('fr-FR')} € - ${result.prix_max.toLocaleString('fr-FR')} €</div>
                <div class="details">
                    <div><div class="label">Prix au m²</div><div class="value">${result.prix_m2_zone.toLocaleString('fr-FR')} €</div></div>
                    <div><div class="label">Score confiance</div><div class="value">${(result.score_confiance * 100).toFixed(0)}%</div></div>
                    <div><div class="label">Surface</div><div class="value">${data.surface_m2} m²</div></div>
                </div>
                <div style="margin-top:24px; display:flex; gap:12px; justify-content:center;">
                    <button class="btn btn-primary" onclick="contactAgent()">Être contacté</button>
                    <button class="btn btn-outline" onclick="mettreEnVente()">Mettre en vente</button>
                </div>
            </div>
        `;
    } catch (error) {
        document.querySelector('#resultContent').innerHTML = `
            <div class="result-box" style="border:2px solid #d32f2f;">
                <p style="color:#d32f2f;">❌ Erreur lors de l'estimation</p>
                <p style="font-size:14px; color:#666;">${error.message}</p>
                <button class="btn btn-primary" onclick="goToStep(3)">Réessayer</button>
            </div>
        `;
    }
}

function contactAgent() {
    alert('📞 Un agent Ymmo vous contactera dans les plus brefs délais.');
}

function mettreEnVente() {
    if (!localStorage.getItem('ymmo_token')) {
        alert('🔒 Veuillez vous connecter pour mettre votre bien en vente.');
        window.location.href = 'login.html';
        return;
    }
    alert('✅ Votre bien a été ajouté en brouillon. Complétez les détails dans le dashboard.');
}