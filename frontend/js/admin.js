const token = localStorage.getItem('ymmo_token');
let agencesCache = [];
let usersCache = [];

const PANEL_TITLES = {
    overview: "Vue d'ensemble",
    users: "Gestion des utilisateurs",
    agences: "Gestion des agences",
    biens: "Gestion des biens",
    contacts: "Messages de contact",
    estimations: "Estimations ML",
};

function getHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    };
}

function showToast(message, type = 'success') {
    const el = document.getElementById('toast');
    el.textContent = message;
    el.className = `toast ${type}`;
    setTimeout(() => { el.className = 'toast'; }, 3000);
}

async function apiFetch(path, options = {}) {
    const response = await fetch(`${API_URL}${path}`, {
        ...options,
        headers: { ...getHeaders(), ...options.headers },
    });
    const data = response.ok ? await response.json().catch(() => ({})) : await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.detail || 'Erreur serveur');
    }
    return data;
}

async function checkAdminAuth() {
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    try {
        const user = await apiFetch('/auth/me');
        if (user.role !== 'admin') {
            window.location.href = 'dashboard.html';
            return false;
        }
        localStorage.setItem('ymmo_user', JSON.stringify(user));
        document.getElementById('userInfo').textContent =
            `Connecté en tant que ${user.prenom || ''} ${user.nom || ''} (${user.email}) — Administrateur`;
        return true;
    } catch {
        logout();
        return false;
    }
}

function showPanel(name) {
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.admin-nav button').forEach(b => b.classList.remove('active'));
    document.getElementById(`panel-${name}`).classList.add('active');
    document.querySelector(`[data-panel="${name}"]`).classList.add('active');
    document.getElementById('panelTitle').textContent = PANEL_TITLES[name] || name;

    const loaders = {
        overview: loadStats,
        users: loadUsers,
        agences: loadAgences,
        biens: loadBiens,
        contacts: loadContacts,
        estimations: loadEstimations,
    };
    if (loaders[name]) loaders[name]();
}

function roleBadge(role) {
    return `<span class="badge badge-${role}">${role}</span>`;
}

function statutBadge(statut) {
    return `<span class="badge badge-${statut}">${statut}</span>`;
}

function formatDate(d) {
    if (!d) return '—';
    return new Date(d).toLocaleDateString('fr-FR');
}

function formatPrice(n) {
    return (n || 0).toLocaleString('fr-FR') + ' €';
}

async function loadStats() {
    try {
        const stats = await apiFetch('/admin/stats');
        document.getElementById('statsGrid').innerHTML = [
            { n: stats.total_users, l: 'Utilisateurs' },
            { n: stats.total_agents, l: 'Agents' },
            { n: stats.total_agences, l: 'Agences' },
            { n: stats.total_biens, l: 'Biens' },
            { n: stats.biens_vente, l: 'En vente' },
            { n: stats.biens_vendus, l: 'Vendus' },
            { n: stats.contacts_nouveaux, l: 'Contacts nouveaux' },
            { n: stats.total_estimations, l: 'Estimations ML' },
            { n: stats.total_vues, l: 'Vues totales' },
        ].map(s => `
            <div class="stat-card">
                <div class="number">${s.n}</div>
                <div class="label">${s.l}</div>
            </div>
        `).join('');
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function loadUsers() {
    try {
        [usersCache, agencesCache] = await Promise.all([
            apiFetch('/admin/users'),
            agencesCache.length ? Promise.resolve(agencesCache) : apiFetch('/admin/agences'),
        ]);
        const agenceName = (id) => agencesCache.find(a => a.id === id)?.nom || '—';
        document.getElementById('usersTable').innerHTML = usersCache.map(u => `
            <tr>
                <td>${u.prenom || ''} ${u.nom || ''}</td>
                <td>${u.email}</td>
                <td>${roleBadge(u.role)}</td>
                <td>${agenceName(u.agence_id)}</td>
                <td>${formatDate(u.date_inscription)}</td>
                <td>
                    <button class="btn-sm btn-edit" onclick="openUserModal(${u.id})">Modifier</button>
                    <button class="btn-sm btn-delete" onclick="deleteUser(${u.id})">Supprimer</button>
                </td>
            </tr>
        `).join('') || '<tr><td colspan="6">Aucun utilisateur</td></tr>';
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function loadAgences() {
    try {
        agencesCache = await apiFetch('/admin/agences');
        document.getElementById('agencesTable').innerHTML = agencesCache.map(a => `
            <tr>
                <td>${a.nom}</td>
                <td>${a.ville}</td>
                <td>${a.adresse}</td>
                <td>${a.telephone || '—'}</td>
                <td>${a.email_contact || '—'}</td>
                <td>
                    <button class="btn-sm btn-edit" onclick="openAgenceModal(${a.id})">Modifier</button>
                    <button class="btn-sm btn-delete" onclick="deleteAgence(${a.id})">Supprimer</button>
                </td>
            </tr>
        `).join('') || '<tr><td colspan="6">Aucune agence</td></tr>';
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function loadBiens() {
    try {
        const biens = await apiFetch('/admin/biens?limit=200');
        document.getElementById('biensTable').innerHTML = biens.map(b => `
            <tr>
                <td>${b.titre}</td>
                <td>${b.ville}</td>
                <td>${formatPrice(b.prix)}</td>
                <td>${b.type}</td>
                <td>${statutBadge(b.statut)}</td>
                <td>${b.nb_vues || 0}</td>
                <td>
                    <button class="btn-sm btn-edit" onclick="openBienModal(${b.id})">Modifier</button>
                    <button class="btn-sm btn-delete" onclick="deleteBien(${b.id})">Supprimer</button>
                </td>
            </tr>
        `).join('') || '<tr><td colspan="7">Aucun bien</td></tr>';
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function loadContacts() {
    try {
        const contacts = await apiFetch('/admin/contacts?limit=200');
        document.getElementById('contactsTable').innerHTML = contacts.map(c => `
            <tr>
                <td>${c.nom}</td>
                <td>${c.email}</td>
                <td>#${c.bien_id}</td>
                <td>${(c.message || '').substring(0, 50)}...</td>
                <td>${statutBadge(c.statut)}</td>
                <td>${formatDate(c.date_envoi)}</td>
                <td>
                    <button class="btn-sm btn-status" onclick="updateContactStatut(${c.id}, 'lu')">Lu</button>
                    <button class="btn-sm btn-status" onclick="updateContactStatut(${c.id}, 'traite')">Traité</button>
                </td>
            </tr>
        `).join('') || '<tr><td colspan="7">Aucun contact</td></tr>';
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function loadEstimations() {
    try {
        const estimations = await apiFetch('/admin/estimations?limit=200');
        document.getElementById('estimationsTable').innerHTML = estimations.map(e => `
            <tr>
                <td>${e.ville} (${e.code_postal})</td>
                <td>${e.type_bien}</td>
                <td>${e.surface_m2} m²</td>
                <td>${e.nb_pieces}</td>
                <td>${formatPrice(e.prix_estime)}</td>
                <td>${formatPrice(e.prix_min)} – ${formatPrice(e.prix_max)}</td>
                <td>${Math.round((e.score_confiance || 0) * 100)}%</td>
                <td>${formatDate(e.date_estimation)}</td>
            </tr>
        `).join('') || '<tr><td colspan="8">Aucune estimation</td></tr>';
    } catch (e) {
        showToast(e.message, 'error');
    }
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('active');
}

async function openUserModal(userId = null) {
    if (!agencesCache.length) agencesCache = await apiFetch('/admin/agences');
    const user = userId ? usersCache.find(u => u.id === userId) : null;
    const agenceOptions = agencesCache.map(a =>
        `<option value="${a.id}" ${user?.agence_id === a.id ? 'selected' : ''}>${a.nom} (${a.ville})</option>`
    ).join('');

    document.getElementById('modalContent').innerHTML = `
        <h3>${user ? 'Modifier utilisateur' : 'Nouvel utilisateur'}</h3>
        <form id="userForm" class="form-grid">
            <div class="form-group">
                <label>Prénom</label>
                <input name="prenom" value="${user?.prenom || ''}" required>
            </div>
            <div class="form-group">
                <label>Nom</label>
                <input name="nom" value="${user?.nom || ''}" required>
            </div>
            <div class="form-group full">
                <label>Email</label>
                <input name="email" type="email" value="${user?.email || ''}" required>
            </div>
            <div class="form-group">
                <label>Rôle</label>
                <select name="role">
                    <option value="client" ${user?.role === 'client' ? 'selected' : ''}>Client</option>
                    <option value="agent" ${user?.role === 'agent' ? 'selected' : ''}>Agent</option>
                    <option value="admin" ${user?.role === 'admin' ? 'selected' : ''}>Admin</option>
                </select>
            </div>
            <div class="form-group">
                <label>Agence</label>
                <select name="agence_id">
                    <option value="">— Aucune —</option>
                    ${agenceOptions}
                </select>
            </div>
            <div class="form-group full">
                <label>${user ? 'Nouveau mot de passe (optionnel)' : 'Mot de passe'}</label>
                <input name="mot_de_passe" type="password" ${user ? '' : 'required minlength="8"'}>
            </div>
        </form>
        <div class="modal-actions">
            <button class="btn btn-outline" onclick="closeModal()">Annuler</button>
            <button class="btn btn-primary" onclick="saveUser(${userId || 'null'})">Enregistrer</button>
        </div>
    `;
    document.getElementById('modalOverlay').classList.add('active');
}

async function saveUser(userId) {
    const form = document.getElementById('userForm');
    const fd = new FormData(form);
    const body = Object.fromEntries(fd.entries());
    if (body.agence_id === '') body.agence_id = null;
    else body.agence_id = parseInt(body.agence_id);
    if (!body.mot_de_passe) delete body.mot_de_passe;

    try {
        if (userId) {
            await apiFetch(`/admin/users/${userId}`, { method: 'PUT', body: JSON.stringify(body) });
        } else {
            if (!body.mot_de_passe) throw new Error('Mot de passe requis');
            await apiFetch('/admin/users', { method: 'POST', body: JSON.stringify(body) });
        }
        closeModal();
        showToast('Utilisateur enregistré');
        loadUsers();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function deleteUser(id) {
    if (!confirm('Supprimer cet utilisateur ?')) return;
    try {
        await apiFetch(`/admin/users/${id}`, { method: 'DELETE' });
        showToast('Utilisateur supprimé');
        loadUsers();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function openAgenceModal(agenceId = null) {
    const agence = agenceId ? agencesCache.find(a => a.id === agenceId) : null;
    document.getElementById('modalContent').innerHTML = `
        <h3>${agence ? 'Modifier agence' : 'Nouvelle agence'}</h3>
        <form id="agenceForm" class="form-grid">
            <div class="form-group">
                <label>Nom</label>
                <input name="nom" value="${agence?.nom || ''}" required>
            </div>
            <div class="form-group">
                <label>Ville</label>
                <input name="ville" value="${agence?.ville || ''}" required>
            </div>
            <div class="form-group full">
                <label>Adresse</label>
                <input name="adresse" value="${agence?.adresse || ''}" required>
            </div>
            <div class="form-group">
                <label>Téléphone</label>
                <input name="telephone" value="${agence?.telephone || ''}">
            </div>
            <div class="form-group">
                <label>Email contact</label>
                <input name="email_contact" type="email" value="${agence?.email_contact || ''}">
            </div>
        </form>
        <div class="modal-actions">
            <button class="btn btn-outline" onclick="closeModal()">Annuler</button>
            <button class="btn btn-primary" onclick="saveAgence(${agenceId || 'null'})">Enregistrer</button>
        </div>
    `;
    document.getElementById('modalOverlay').classList.add('active');
}

async function saveAgence(agenceId) {
    const form = document.getElementById('agenceForm');
    const body = Object.fromEntries(new FormData(form).entries());
    try {
        if (agenceId) {
            await apiFetch(`/admin/agences/${agenceId}`, { method: 'PUT', body: JSON.stringify(body) });
        } else {
            await apiFetch('/admin/agences', { method: 'POST', body: JSON.stringify(body) });
        }
        closeModal();
        showToast('Agence enregistrée');
        loadAgences();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function deleteAgence(id) {
    if (!confirm('Supprimer cette agence ?')) return;
    try {
        await apiFetch(`/admin/agences/${id}`, { method: 'DELETE' });
        showToast('Agence supprimée');
        loadAgences();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function openBienModal(bienId) {
    const biens = await apiFetch('/admin/biens?limit=200');
    const bien = biens.find(b => b.id === bienId);
    if (!agencesCache.length) agencesCache = await apiFetch('/admin/agences');
    const agenceOptions = agencesCache.map(a =>
        `<option value="${a.id}" ${bien.agence_id === a.id ? 'selected' : ''}>${a.nom}</option>`
    ).join('');

    document.getElementById('modalContent').innerHTML = `
        <h3>Modifier bien #${bienId}</h3>
        <form id="bienForm" class="form-grid">
            <div class="form-group full">
                <label>Titre</label>
                <input name="titre" value="${bien.titre}" required>
            </div>
            <div class="form-group">
                <label>Prix (€)</label>
                <input name="prix" type="number" value="${bien.prix}" required>
            </div>
            <div class="form-group">
                <label>Surface (m²)</label>
                <input name="surface_m2" type="number" value="${bien.surface_m2}" required>
            </div>
            <div class="form-group">
                <label>Ville</label>
                <input name="ville" value="${bien.ville}" required>
            </div>
            <div class="form-group">
                <label>Code postal</label>
                <input name="code_postal" value="${bien.code_postal}" required>
            </div>
            <div class="form-group">
                <label>Type</label>
                <select name="type">
                    <option value="maison" ${bien.type === 'maison' ? 'selected' : ''}>Maison</option>
                    <option value="appartement" ${bien.type === 'appartement' ? 'selected' : ''}>Appartement</option>
                    <option value="commerce" ${bien.type === 'commerce' ? 'selected' : ''}>Commerce</option>
                </select>
            </div>
            <div class="form-group">
                <label>Statut</label>
                <select name="statut">
                    <option value="vente" ${bien.statut === 'vente' ? 'selected' : ''}>Vente</option>
                    <option value="location" ${bien.statut === 'location' ? 'selected' : ''}>Location</option>
                    <option value="vendu" ${bien.statut === 'vendu' ? 'selected' : ''}>Vendu</option>
                </select>
            </div>
            <div class="form-group">
                <label>Agence</label>
                <select name="agence_id">${agenceOptions}</select>
            </div>
        </form>
        <div class="modal-actions">
            <button class="btn btn-outline" onclick="closeModal()">Annuler</button>
            <button class="btn btn-primary" onclick="saveBien(${bienId})">Enregistrer</button>
        </div>
    `;
    document.getElementById('modalOverlay').classList.add('active');
}

async function saveBien(bienId) {
    const form = document.getElementById('bienForm');
    const body = Object.fromEntries(new FormData(form).entries());
    body.prix = parseFloat(body.prix);
    body.surface_m2 = parseFloat(body.surface_m2);
    body.agence_id = parseInt(body.agence_id);
    try {
        await apiFetch(`/admin/biens/${bienId}`, { method: 'PUT', body: JSON.stringify(body) });
        closeModal();
        showToast('Bien mis à jour');
        loadBiens();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function deleteBien(id) {
    if (!confirm('Supprimer ce bien ?')) return;
    try {
        await apiFetch(`/admin/biens/${id}`, { method: 'DELETE' });
        showToast('Bien supprimé');
        loadBiens();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function updateContactStatut(id, statut) {
    try {
        await apiFetch(`/contacts/${id}/statut?statut=${statut}`, { method: 'PUT' });
        showToast(`Contact marqué "${statut}"`);
        loadContacts();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

function logout() {
    localStorage.removeItem('ymmo_token');
    localStorage.removeItem('ymmo_user');
    window.location.href = 'login.html';
}

document.getElementById('modalOverlay').addEventListener('click', (e) => {
    if (e.target.id === 'modalOverlay') closeModal();
});

(async () => {
    if (await checkAdminAuth()) {
        loadStats();
    }
})();
