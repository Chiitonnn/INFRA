let currentPage = 1;
const perPage = 8;
let totalPages = 1;

async function loadBiens(params = {}) {
    const container = document.getElementById('biensContainer');
    container.innerHTML = '<div class="no-results">Chargement...</div>';

    const query = new URLSearchParams({
        skip: (currentPage - 1) * perPage,
        limit: perPage,
        ...params
    });

    try {
        const response = await fetch(`${API_URL}/biens/?${query}`);
        if (!response.ok) throw new Error('Erreur API');
        const biens = await response.json();
        displayBiens(biens);
        updatePagination(biens.length);
    } catch (error) {
        container.innerHTML = `<div class="no-results"><div class="icon">❌</div><p>Erreur de chargement</p></div>`;
    }
}

function displayBiens(biens) {
    const container = document.getElementById('biensContainer');
    if (!biens || biens.length === 0) {
        container.innerHTML = `
            <div class="no-results" style="grid-column:1/-1;">
                <div class="icon">🏠</div>
                <p>Aucun bien trouvé</p>
                <button class="btn btn-primary" onclick="resetFilters()">Voir tous les biens</button>
            </div>
        `;
        return;
    }

    container.innerHTML = biens.map(b => {
        const isAppartementTest = b.titre && b.titre.toLowerCase().includes('appartement test');
        const imgSrc = isAppartementTest 
            ? 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=400&q=80'
            : `https://picsum.photos/seed/${b.id}/400/300`;
            
        return `
        <div class="bien-card" onclick="window.location.href='bien.html?id=${b.id}'">
            <img src="${imgSrc}" alt="${b.titre || 'Bien'}">
            <div class="content">
                <div class="price">${b.prix?.toLocaleString('fr-FR') || '0'} €</div>
                <div class="title">${b.titre || 'Sans titre'}</div>
                <div class="location">${b.ville || ''} ${b.code_postal || ''}</div>
                <div class="details">
                    <span>${b.surface_m2 || 0} m²</span>
                    <span>${b.nb_pieces || 0} pièces</span>
                    <span class="badge ${b.statut || 'vente'}">${b.statut || 'vente'}</span>
                </div>
            </div>
        </div>
    `;
    }).join('');
}

function updatePagination(count) {
    const pagination = document.getElementById('pagination');
    if (count < perPage && currentPage === 1) {
        pagination.innerHTML = '';
        return;
    }
    const prev = currentPage > 1 ? `<button onclick="changePage(${currentPage - 1})">‹</button>` : '';
    const next = count === perPage ? `<button onclick="changePage(${currentPage + 1})">›</button>` : '';
    pagination.innerHTML = `${prev}<span style="padding:8px 12px;">Page ${currentPage}</span>${next}`;
}

function changePage(page) {
    currentPage = page;
    applyFilters();
}

function applyFilters() {
    const params = {
        ville: document.getElementById('filter_ville').value,
        type_bien: document.getElementById('filter_type').value,
        prix_min: document.getElementById('filter_prix_min').value || undefined,
        prix_max: document.getElementById('filter_prix_max').value || undefined,
        surface_min: document.getElementById('filter_surface_min').value || undefined,
        surface_max: document.getElementById('filter_surface_max').value || undefined
    };
    loadBiens(params);
}

function resetFilters() {
    document.getElementById('filter_ville').value = '';
    document.getElementById('filter_type').value = '';
    document.getElementById('filter_prix_min').value = '';
    document.getElementById('filter_prix_max').value = '';
    document.getElementById('filter_surface_min').value = '';
    document.getElementById('filter_surface_max').value = '';
    currentPage = 1;
    loadBiens();
}

// Charger au démarrage
function getInitialParams() {
    const urlParams = new URLSearchParams(window.location.search);
    const params = {};
    if (urlParams.has('ville')) {
        params.ville = urlParams.get('ville');
        document.getElementById('filter_ville').value = params.ville;
    }
    if (urlParams.has('prix_min') && urlParams.get('prix_min')) {
        params.prix_min = urlParams.get('prix_min');
        document.getElementById('filter_prix_min').value = params.prix_min;
    }
    if (urlParams.has('prix_max') && urlParams.get('prix_max')) {
        params.prix_max = urlParams.get('prix_max');
        document.getElementById('filter_prix_max').value = params.prix_max;
    }
    return params;
}

loadBiens(getInitialParams());
