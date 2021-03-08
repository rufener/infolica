# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc
from pyramid.response import FileResponse

from infolica.exceptions.custom_error import CustomError
from infolica.models.constant import Constant
from infolica.models.models import Affaire, AffaireType, ModificationAffaireType
from infolica.models.models import ModificationAffaire, VAffaire, Facture
from infolica.models.models import ControleGeometre, ControleMutation, ControlePPE, SuiviMandat
from infolica.models.models import AffaireEtape
from infolica.scripts.utils import Utils

from sqlalchemy import and_, or_

import os
import json
from datetime import datetime, timedelta
from docxtpl import DocxTemplate, RichText

###########################################################
# AFFAIRE
###########################################################


@view_config(route_name='affaires', request_method='GET', renderer='json')
@view_config(route_name='affaires_s', request_method='GET', renderer='json')
def affaires_view(request):
    """
    Return all affaires
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    query = request.dbsession.query(VAffaire).order_by(VAffaire.id.desc()).all()
    return Utils.serialize_many(query)


@view_config(route_name='affaire_by_id', request_method='GET', renderer='json')
def affaire_by_id_view(request):
    """
    Return affaires by id
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    id = request.matchdict['id']
    query = request.dbsession.query(VAffaire)
    one = query.filter(VAffaire.id == id).first()
    return Utils.serialize_one(one)


@view_config(route_name='affaires_cockpit', request_method='GET', renderer='json')
def affaire_cockpit_view(request):
    """
    Return active affaires (id, no_access, id_current_step)
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    type_id = request.params['type_id'] if 'type_id' in request.params else None
    etape_id = request.params['etape_id'] if 'etape_id' in request.params else None

    affaire_show_timedelta = int(request.registry.settings['affaire_show_timedelta'])
    since = datetime.date(datetime.now()) - timedelta(days=affaire_show_timedelta)
    
    etape_mat_diff_id = int(request.registry.settings['affaire_etape_mat_diff_id'])

    query = request.dbsession.query(VAffaire)
    
    if type_id is not None:
        query = query.filter(VAffaire.type_id == type_id)
    else:
        query = query.filter(VAffaire.etape_id != None)
    
    if etape_id is not None:
        query = query.filter(VAffaire.etape_id == etape_id)
    else:
        query = query.filter(or_(
            VAffaire.etape_id == etape_mat_diff_id,
            and_(
                or_(
                    VAffaire.date_envoi >= since,
                    VAffaire.date_envoi == None
                ),
                VAffaire.date_cloture == None
            )
        ))
    
    query = query.all()

    affaires = []
    for affaire in query:
        affaires.append({
            'id': affaire.id,
            'affaire_type': affaire.type_affaire,
            'affaire_type_id': affaire.type_id,
            'no_access': affaire.no_access,
            'etape_id': affaire.etape_id,
            'etape_ordre': affaire.etape_ordre,
            'etape_datetime': datetime.strftime(affaire.etape_datetime, '%Y-%m-%d %H:%M:%S'),
            'operateur_id': affaire.technicien_id,
            'operateur_initiales': affaire.technicien_initiales,
            'cadastre': affaire.cadastre,
            'description': affaire.nom
        })
    
    return json.dumps(affaires)


@view_config(route_name='recherche_affaires', request_method='POST', renderer='json')
@view_config(route_name='recherche_affaires_s', request_method='POST', renderer='json')
def affaires_search_view(request):
    """
    Search affaires
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    settings = request.registry.settings
    search_limit = int(settings['search_limit'])
    
    params_affaires = {}
    client = None
    client_in_params = False
    for key in request.params.keys():
        if "client" in key:
            client = request.params[key]
            client_in_params = True
            params_affaires["client_commande_id"] = request.params[key]
            params_affaires["client_envoi_id"] = request.params[key]
        else:
            params_affaires[key] = request.params[key]
    
    # Chercher les affaires par les clients de facture
    affaires_id_by_clients_facture = []
    if client_in_params:
        query_facture = request.dbsession.query(Facture).filter(or_(
            Facture.client_id == client,
            Facture.client_co_id == client,
        )).all()

        # Récupérer la liste des id des affaires retenues
        for facture in query_facture:
            affaires_id_by_clients_facture.append(int(facture.affaire_id))
    
    # Chercher les affaires par les conditions (sauf client_facture)
    conditions = Utils.get_search_conditions(VAffaire, params_affaires)
    query = request.dbsession.query(VAffaire)
    if client_in_params:
        query = query.filter(and_(
            *conditions,
            VAffaire.id.in_(affaires_id_by_clients_facture)
        ))
    else:
        query = query.filter(*conditions)



    query = query.limit(search_limit).all()
    return Utils.serialize_many(query)


@view_config(route_name='types_affaires', request_method='GET', renderer='json')
@view_config(route_name='types_affaires_s', request_method='GET', renderer='json')
def types_affaires_view(request):
    """
    Return all types affaires not modif
    """
    affaire_type_modif_threshold = int(request.registry.settings['affaire_type_modification_ordre_separation'])

    types_affaires = request.dbsession.query(AffaireType).filter(
        and_(
            AffaireType.ordre != None,
            AffaireType.ordre < affaire_type_modif_threshold
        )
    ).order_by(AffaireType.ordre.asc()).all()

    types_affaires = Utils.serialize_many(types_affaires)
    return types_affaires


@view_config(route_name='types_modification_affaire', request_method='GET', renderer='json')
@view_config(route_name='types_modification_affaire_s', request_method='GET', renderer='json')
def types_modification_affaire_view(request):
    """
    Return all types modification affaire
    """
    records = request.dbsession.query(ModificationAffaireType).filter(
        ModificationAffaireType.ordre != None
    ).order_by(ModificationAffaireType.ordre.asc()).all()

    return Utils.serialize_many(records)


@view_config(route_name='affaires', request_method='POST', renderer='json')
@view_config(route_name='affaires_s', request_method='POST', renderer='json')
def affaires_new_view(request):
    """
    Add new affaire
    """
    # Get role depending on affaire type
    affaire_type = request.params['type_id'] if 'type_id' in request.params else None

    # Permission (fonction) par défaut
    permission = request.registry.settings['affaire_edition']

    # Affaire de cadastration
    if affaire_type == request.registry.settings['affaire_type_cadastration_id']:
        permission = request.registry.settings['affaire_cadastration_edition']
    # Affaire de PPE
    elif affaire_type == request.registry.settings['affaire_type_ppe_id']:
        permission = request.registry.settings['affaire_ppe_edition']
    # Affaire de révision d'abornement
    elif affaire_type == request.registry.settings['affaire_type_revision_abornement_id']:
        permission = request.registry.settings['affaire_revision_abornement_edition']
    # Affaire de rétablissement de PFP3
    elif affaire_type == request.registry.settings['affaire_type_retablissement_pfp3_id']:
        permission = request.registry.settings['affaire_retablissement_pfp3_edition']
    # Affaire pcop
    elif affaire_type == request.registry.settings['affaire_type_part_copropriete_id']:
        permission = request.registry.settings['affaire_pcop_edition']
    # Affaire autre
    elif affaire_type == request.registry.settings['affaire_type_autre_id']:
        permission = request.registry.settings['affaire_autre_edition']

    # Check authorization
    if not Utils.has_permission(request, permission):
        raise exc.HTTPForbidden()

    model = Affaire()
    model = Utils.set_model_record(model, request.params)

    request.dbsession.add(model)
    # Récupèrer l'id de la nouvelle affaire
    request.dbsession.flush()

    # Créer le chemin du dossier de l'affaire
    model.chemin = os.path.join(request.registry.settings['affaires_directory_dev'], str(model.id))

    # Copier le dossier __template pour une nouvelle affaire
    Utils.create_affaire_folder(request, model.chemin)


    # Créer les formulaires de contrôle
    params = {'affaire_id': model.id}
    if not model.type_id in [int(request.registry.settings['affaire_type_part_copropriete_id']), int(request.registry.settings['affaire_type_autre_id'])]:
        if model.type_id == int(request.registry.settings['affaire_type_ppe_id']):
            # Create controle PPE
            Utils.addNewRecord(request, ControlePPE, params)
        else:
            # Create controle Mutation
            Utils.addNewRecord(request, ControleMutation, params)
        
        Utils.addNewRecord(request, SuiviMandat, params)
        Utils.addNewRecord(request, ControleGeometre, params)


    # Créer l'étape de création d'affaire
    params['etape_id'] = request.registry.settings['affaire_premiere_etape_defaut_id']
    tmp = request.dbsession.query(AffaireType).filter(AffaireType.id == model.type_id).first()
    if tmp and tmp.logique_processus:
        if len(tmp.logique_processus) > 0:
            params['etape_id'] = tmp.logique_processus[0]
    
    params['operateur_id'] = request.params['operateur_id'] if 'operateur_id' in request.params else None
    params['datetime'] = datetime.now()
    Utils.addNewRecord(request, AffaireEtape, params)


    # Add facture
    if 'facture_client_id' in request.params:
        params = {
            'type_id': request.registry.settings['facture_type_facture_id'],
            'affaire_id': model.id,
            'client_id': request.params['facture_client_id'],
            'client_co_id': request.params['facture_client_co_id'] if 'facture_client_co_id' in request.params else None,
            'client_complement': request.params['facture_client_complement'] if 'facture_client_complement' in request.params else None,
            'client_premiere_ligne': request.params['facture_client_premiere_ligne'] if 'facture_client_premiere_ligne' in request.params else None,
            'montant_mo': 0,
            'montant_rf': 0,
            'montant_mat_diff': 0,
            'montant_tva': 0,
            'montant_total': 0
        }
        Utils.addNewRecord(request, Facture, params)

    return model.id


@view_config(route_name='affaires', request_method='PUT', renderer='json')
@view_config(route_name='affaires_s', request_method='PUT', renderer='json')
def affaires_update_view(request):
    """
    Update affaire
    """
    # id_affaire
    id_affaire = request.params['id_affaire'] if 'id_affaire' in request.params else None

    # Get the affaire
    record = request.dbsession.query(Affaire).filter(
        Affaire.id == id_affaire).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(Affaire.__tablename__, id_affaire))

    # Get role depending on affaire type
    affaire_type = request.params['type_id'] if 'type_id' in request.params else record.type_id

    # Permission (fonction) par défaut
    permission = request.registry.settings['affaire_edition']

    # Affaire de cadastration
    if affaire_type == request.registry.settings['affaire_type_cadastration_id']:
        permission = request.registry.settings['affaire_cadastration_edition']
    # Affaire de PPE
    elif affaire_type == request.registry.settings['affaire_type_ppe_id']:
        permission = request.registry.settings['affaire_ppe_edition']
    # Affaire de révision d'abornement
    elif affaire_type == request.registry.settings['affaire_type_revision_abornement_id']:
        permission = request.registry.settings['affaire_revision_abornement_edition']
    # Affaire de rétablissement de PFP3
    elif affaire_type == request.registry.settings['affaire_type_retablissement_pfp3_id']:
        permission = request.registry.settings['affaire_retablissement_pfp3_edition']

    # Check authorization
    if not Utils.has_permission(request, permission):
        raise exc.HTTPForbidden()

    record = Utils.set_model_record(record, request.params)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Affaire.__tablename__))


@view_config(route_name='courrier_affaire', request_method='POST', renderer='json')
@view_config(route_name='courrier_affaire_s', request_method='POST', renderer='json')
def courrier_affaire_view(request):
    """
    Create  file
    """
    settings = request.registry.settings
    mails_templates_directory = settings['mails_templates_directory']
    temporary_directory = settings['temporary_directory']

    # Get request params
    template = request.params['template']
    values = request.params['values']
    output_file_name = request.params['output_file_name'] if 'output_file_name' in request.params else template

    # Set output file name
    date_time = datetime.now().strftime("%Y%m%d")
    filename = output_file_name + "_" + date_time + '.docx'
    file_path = os.path.join(temporary_directory, filename)

    # Set context
    context = json.loads(values)
    for key in context.keys():
        context[key] = RichText(context[key])

    # Ouverture du document template
    doc = DocxTemplate(os.path.join(mails_templates_directory, template + ".docx"))

    # Replace values by keywords and save
    doc.render(context)
    doc.save(file_path)

    return {'filename': filename}


@view_config(route_name='courrier_affaire', request_method='GET')
@view_config(route_name='courrier_affaire_s', request_method='GET')
def download_courrier_affaire_view(request):
    """
    Send file
    """
    settings = request.registry.settings
    filename = request.params['filename']
    temporary_directory = settings["temporary_directory"]
    file_path = os.path.join(temporary_directory, filename)

    if os.path.exists(file_path):
        response = FileResponse(file_path, request=request, cache_max_age=86400)
        headers = response.headers
        headers['Content-Type'] = 'application/download'
        headers['Accept-Ranges'] = 'bite'
        headers['Content-Disposition'] = 'attachment;filename=' + filename

        return response

    else:
        raise exc.HTTPNotFound("Le fichier est indisponible")


@view_config(route_name='courrier_affaire', request_method='DELETE', renderer='string')
@view_config(route_name='courrier_affaire_s', request_method='DELETE', renderer='string')
def delete_courrier_affaire_view(request):
    """
    Supprimer le fichier une fois téléchargé
    """
    settings = request.registry.settings
    filename = request.params['filename']
    temporary_directory = settings["temporary_directory"]
    file_path = os.path.join(temporary_directory, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        return "ok"

    else:
        raise exc.HTTPNotFound("Le fichier est indisponible")


@view_config(route_name='modification_affaires', request_method='POST', renderer='json')
@view_config(route_name='modification_affaires_s', request_method='POST', renderer='json')
def modification_affaires_view(request):
    """
    Modification affaire
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_edition']):
        raise exc.HTTPForbidden()

    # Get client instance
    model = Utils.set_model_record(ModificationAffaire(), request.params)

    request.dbsession.add(model)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(ModificationAffaire.__tablename__))


@view_config(route_name="modification_affaire_by_affaire_mere", request_method="GET", renderer="json")
def modification_affaire_by_affaire_mere_view(request):
    """
    Get modification affaire by affaire_mère
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    affaire_mere_id = request.matchdict["id"]

    records = request.dbsession.query(ModificationAffaire).filter(
        ModificationAffaire.affaire_id_fille == affaire_mere_id
    ).all()

    return Utils.serialize_many(records)


@view_config(route_name="modification_affaire_by_affaire_fille", request_method="GET", renderer="json")
def modification_affaire_by_affaire_fille_view(request):
    """
    Get modification affaire by affaire_fille
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    affaire_fille_id = request.matchdict["id"]

    records = request.dbsession.query(ModificationAffaire).filter(
        ModificationAffaire.affaire_id_mere == affaire_fille_id
    ).all()

    return Utils.serialize_many(records)
