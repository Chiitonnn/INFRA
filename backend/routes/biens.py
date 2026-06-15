from flask import Blueprint, request, jsonify
from models import Bien, db

biens_bp = Blueprint('biens_bp', __name__)

@biens_bp.route('/', methods=['GET'])
def get_biens():
    # Application des filtres demandés
    query = Bien.query
    if 'ville' in request.args:
        query = query.filter(Bien.ville.ilike(f"%{request.args['ville']}%"))
    if 'type' in request.args:
        query = query.filter_by(type=request.args['type'])
    if 'prix_max' in request.args:
        query = query.filter(Bien.prix <= float(request.args['prix_max']))
    if 'surface_min' in request.args:
        query = query.filter(Bien.surface_m2 >= float(request.args['surface_min']))

    # Pagination minimaliste 
    page = request.args.get('page', 1, type=int)
    per_page = 20
    biens = query.paginate(page=page, per_page=per_page, error_out=False)

    results = []
    for b in biens.items:
        results.append({
            "id": b.id,
            "titre": b.titre,
            "ville": b.ville,
            "prix": b.prix,
            "surface_m2": b.surface_m2,
            "nb_pieces": b.nb_pieces,
            "type": b.type,
            "statut": b.statut,
            "photos": [p.url for p in b.photos] if b.photos else []
        })

    return jsonify({
        "data": results,
        "total": biens.total,
        "page": biens.page,
        "pages": biens.pages
    })

@biens_bp.route('/<int:bien_id>', methods=['GET'])
def get_bien_detail(bien_id):
    b = Bien.query.get_or_404(bien_id)
    return jsonify({
        "id": b.id,
        "titre": b.titre,
        "description": b.description,
        "prix": b.prix,
        "surface_m2": b.surface_m2,
        "ville": b.ville,
        "code_postal": b.code_postal,
        "dpe": b.dpe,
        "annee_construction": b.annee_construction,
        "etat_general": b.etat_general,
        "latitude": b.latitude,
        "longitude": b.longitude,
        "agent_id": b.agent_id
    })
