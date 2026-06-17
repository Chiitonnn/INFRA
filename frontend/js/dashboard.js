let token = localStorage.getItem('ymmo_token');

function getHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
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
        if (user.role === 'admin') {
            // Admin can view the agent dashboard, don't redirect
        }
        if (user.role === 'client') {
            // Client can view the dashboard, don't redirect
        }
        return true;
    } catch (error) {
        logout();
        return false;
    }
}

async function loadDashboard() {
    if (!await checkAuth()) return;

    try {
        // Charger les biens
        const biensRes = await fetch(`${API_URL}/biens/`, { headers: getHeaders() });
        const biens = await biensRes.json();

        // Charger les contacts
        const contactsRes = await fetch(`${API_URL}/contacts/`, { headers: getHeaders() });
        const contacts = contactsRes.ok ? await contactsRes.json() : [];

        updateStats(biens, contacts);
        renderBiens(biens);
        renderContacts(contacts);

        // Info utilisateur
        const user = JSON.parse(localStorage.getItem('ymmo_user') || '{}');
        document.getElementById('userInfo').textContent = `Connecté en tant que ${user.email || 'utilisateur'}`;

    } catch (error) {
        console.error('Erreur:', error);
        document.getElementById('biensList').innerHTML = '<p style="color:#888;">Erreur de chargement</p>';
        document.getElementById('contactsList').innerHTML = '<p style="color:#888;">Erreur de chargement</p>';
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
        container.innerHTML = '<p style="color:#888;">Aucun bien à afficher</p>';
        return;
    }

    container.innerHTML = biens.slice(0, 10).map(b => `
        <div class="bien-item">
            <div class="info">
                <div class="title">${b.titre || 'Sans titre'}</div>
                <div class="meta">${b.ville || ''} • ${b.prix?.toLocaleString('fr-FR') || 0} € • ${b.statut || 'vente'}</div>
            </div>
            <div class="actions">
                <button onclick="window.location.href='bien.html?id=${b.id}'">Voir</button>
            </div>
        </div>
    `).join('');
}

function renderContacts(contacts) {
    const container = document.getElementById('contactsList');
    if (!contacts || contacts.length === 0) {
        container.innerHTML = '<p style="color:#888;">Aucun message reçu</p>';
        return;
    }

    container.innerHTML = contacts.slice(0, 10).map(c => `
        <div class="contact-item">
            <div class="name">${c.nom || 'Anonyme'} <span class="statut-badge ${c.statut || 'nouveau'}">${c.statut || 'nouveau'}</span></div>
            <div class="bien">${c.message?.substring(0, 60) || ''}...</div>
        </div>
    `).join('');
}

function toggleAddForm() {
    const form = document.getElementById('addForm');
    form.classList.toggle('active');
}

async function submitBien() {
    const data = {
        titre: document.getElementById('add_titre').value,
        ville: document.getElementById('add_ville').value,
        prix: parseFloat(document.getElementById('add_prix').value),
        surface_m2: parseFloat(document.getElementById('add_surface').value),
        type: document.getElementById('add_type').value,
        statut: document.getElementById('add_statut').value,
        nb_pieces: parseInt(document.getElementById('add_pieces').value) || 0,
        code_postal: document.getElementById('add_code_postal').value,
        description: document.getElementById('add_description').value,
        adresse: `${document.getElementById('add_ville').value} ${document.getElementById('add_code_postal').value}`.trim(),
        agence_id: 1
    };

    if (!data.titre || !data.ville || !data.prix || !data.surface_m2 || !data.code_postal) {
        document.getElementById('addResult').textContent = '⚠️ Veuillez remplir tous les champs obligatoires.';
        return;
    }

    try {
        const response = await fetch(`${API_URL}/biens/`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('Erreur création');

        document.getElementById('addResult').textContent = '✅ Bien ajouté !';
        document.getElementById('addResult').style.color = '#2e7d32';
        document.getElementById('addForm').classList.remove('active');
        loadDashboard();

    } catch (error) {
        document.getElementById('addResult').textContent = '❌ ' + error.message;
        document.getElementById('addResult').style.color = '#d32f2f';
    }
}

function logout() {
    localStorage.removeItem('ymmo_token');
    localStorage.removeItem('ymmo_user');
    window.location.href = 'login.html';
}

// Charger au démarrage
loadDashboard();
