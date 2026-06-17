let token = localStorage.getItem('ymmo_token');

function getHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

function showToast(message, type = 'success') {
    const el = document.getElementById('toast');
    el.textContent = message;
    el.className = `toast ${type} show`;
    setTimeout(() => { el.className = 'toast'; }, 3000);
}

async function checkAuth() {
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    try {
        const response = await fetch(`${API_URL}/auth/me`, { headers: getHeaders() });
        if (!response.ok) throw new Error('Session invalide');
        const user = await response.json();
        localStorage.setItem('ymmo_user', JSON.stringify(user));

        // Afficher les infos utilisateur
        const initiales = ((user.prenom?.[0] || '') + (user.nom?.[0] || '')).toUpperCase() || user.email[0].toUpperCase();
        document.getElementById('userAvatar').textContent = initiales;
        document.getElementById('userInfo').textContent = user.prenom ? `${user.prenom} ${user.nom || ''}` : user.email;

        return true;
    } catch (error) {
        logout();
        return false;
    }
}

async function loadDashboard() {
    if (!await checkAuth()) return;

    try {
        // Charger uniquement les biens de l'utilisateur connecté
        const biensRes = await fetch(`${API_URL}/biens/mine`, { headers: getHeaders() });
        const biens = biensRes.ok ? await biensRes.json() : [];

        // Charger les contacts
        const contactsRes = await fetch(`${API_URL}/contacts/`, { headers: getHeaders() });
        const contacts = contactsRes.ok ? await contactsRes.json() : [];

        updateStats(biens, contacts);
        renderBiens(biens);
        renderContacts(contacts);

        // Vérifier si on doit ouvrir le formulaire pré-rempli (depuis estimation)
        checkPrefill();

    } catch (error) {
        console.error('Erreur:', error);
        showToast('Erreur de chargement', 'error');
    }
}

function checkPrefill() {
    const urlParams = new URLSearchParams(window.location.search);
    const prefillData = sessionStorage.getItem('ymmo_prefill');

    if (urlParams.get('action') === 'add' && prefillData) {
        const data = JSON.parse(prefillData);
        sessionStorage.removeItem('ymmo_prefill');

        // Ouvrir et pré-remplir le formulaire
        document.getElementById('addForm').classList.add('active');
        document.getElementById('addToggleBtn').textContent = '✕ Fermer';

        if (data.ville) document.getElementById('add_ville').value = data.ville;
        if (data.code_postal) document.getElementById('add_code_postal').value = data.code_postal;
        if (data.surface_m2) document.getElementById('add_surface').value = data.surface_m2;
        if (data.nb_pieces) document.getElementById('add_pieces').value = data.nb_pieces;
        if (data.prix_estime) document.getElementById('add_prix').value = Math.round(data.prix_estime);
        if (data.type_bien) {
            const sel = document.getElementById('add_type');
            for (let opt of sel.options) {
                if (opt.value === data.type_bien) { opt.selected = true; break; }
            }
        }

        // Pré-remplir le titre
        const typeLabel = { 'maison': 'Maison', 'appartement': 'Appartement', 'commerce': 'Local commercial' };
        document.getElementById('add_titre').value = `${typeLabel[data.type_bien] || 'Bien'} à ${data.ville || ''}`;

        showToast('Formulaire pré-rempli avec votre estimation ✨', 'success');

        // Scroll vers le formulaire
        setTimeout(() => {
            document.getElementById('addForm').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
    }
}

function updateStats(biens, contacts) {
    const total = biens.length || 0;
    const vendus = biens.filter(b => b.statut === 'vendu').length || 0;
    const vues = biens.reduce((acc, b) => acc + (b.nb_vues || 0), 0);
    const nonTraites = contacts.filter(c => c.statut === 'nouveau').length || 0;

    document.getElementById('statBiens').textContent = total;
    document.getElementById('statVendus').textContent = vendus;
    document.getElementById('statContacts').textContent = nonTraites;
    document.getElementById('statVues').textContent = vues;
}

function renderBiens(biens) {
    const container = document.getElementById('biensList');
    if (!biens || biens.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">🏡</div>
                <p>Aucun bien pour l'instant.<br>Ajoutez votre premier bien ou estimez-en un !</p>
            </div>`;
        return;
    }

    container.innerHTML = biens.slice(0, 10).map(b => {
        const statutClass = b.statut || 'vente';
        const img = `https://picsum.photos/seed/${b.id}x/100/100`;
        return `
        <div class="bien-item">
            <img class="bien-thumb" src="${img}" alt="${b.titre}" onerror="this.style.display='none'">
            <div class="bien-info">
                <div class="title">${b.titre || 'Sans titre'}</div>
                <div class="meta">${b.ville || ''} · ${(b.prix || 0).toLocaleString('fr-FR')} € · ${b.surface_m2 || 0} m²</div>
                <span class="statut-pill ${statutClass}">${statutClass}</span>
            </div>
            <div class="bien-actions">
                <button class="btn-sm view" onclick="window.location.href='bien.html?id=${b.id}'">Voir</button>
            </div>
        </div>`;
    }).join('');
}

function renderContacts(contacts) {
    const container = document.getElementById('contactsList');
    if (!contacts || contacts.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">💬</div>
                <p>Aucun message reçu.</p>
            </div>`;
        return;
    }

    container.innerHTML = contacts.slice(0, 10).map(c => {
        const badgeClass = c.statut === 'nouveau' ? 'badge-nouveau' : c.statut === 'lu' ? 'badge-lu' : 'badge-traite';
        return `
        <div class="contact-item">
            <div class="name">
                ${c.nom || 'Anonyme'}
                <span class="${badgeClass}">${c.statut || 'nouveau'}</span>
            </div>
            <div class="preview">${(c.message || '').substring(0, 70)}...</div>
        </div>`;
    }).join('');
}

function toggleAddForm() {
    const form = document.getElementById('addForm');
    const btn = document.getElementById('addToggleBtn');
    const isOpen = form.classList.toggle('active');
    btn.textContent = isOpen ? '✕ Fermer' : '+ Ajouter un bien';
    if (isOpen) {
        setTimeout(() => form.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
    }
}

async function submitBien() {
    const titre = document.getElementById('add_titre').value.trim();
    const ville = document.getElementById('add_ville').value.trim();
    const prix = parseFloat(document.getElementById('add_prix').value);
    const surface = parseFloat(document.getElementById('add_surface').value);
    const code_postal = document.getElementById('add_code_postal').value.trim();

    if (!titre || !ville || !prix || !surface || !code_postal) {
        document.getElementById('addResult').innerHTML = '<span style="color:#dc2626;">⚠️ Veuillez remplir tous les champs obligatoires.</span>';
        return;
    }

    const data = {
        titre,
        ville,
        prix,
        surface_m2: surface,
        type: document.getElementById('add_type').value,
        statut: document.getElementById('add_statut').value,
        nb_pieces: parseInt(document.getElementById('add_pieces').value) || 1,
        code_postal,
        description: document.getElementById('add_description').value,
        adresse: `${ville} ${code_postal}`.trim(),
        agence_id: 1
    };

    try {
        const response = await fetch(`${API_URL}/biens/`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Erreur création');
        }

        showToast('✅ Bien ajouté avec succès !', 'success');
        document.getElementById('addForm').classList.remove('active');
        document.getElementById('addToggleBtn').textContent = '+ Ajouter un bien';
        document.getElementById('addResult').innerHTML = '';
        loadDashboard();

    } catch (error) {
        document.getElementById('addResult').innerHTML = `<span style="color:#dc2626;">❌ ${error.message}</span>`;
    }
}

function logout() {
    localStorage.removeItem('ymmo_token');
    localStorage.removeItem('ymmo_user');
    window.location.href = 'login.html';
}

// Charger au démarrage
loadDashboard();
