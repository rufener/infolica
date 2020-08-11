# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc
from pyramid.response import FileResponse

from infolica.exceptions.custom_error import CustomError
from infolica.models.constant import Constant
from infolica.models.models import Affaire, AffaireType, ModificationAffaireType
from infolica.models.models import ModificationAffaire, VAffaire, Facture
from infolica.scripts.utils import Utils

from sqlalchemy import or_

import os
import json
from datetime import datetime
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
    if len(affaires_id_by_clients_facture) > 0:
        query = query.filter(or_(
            *conditions,
            VAffaire.id.in_(affaires_id_by_clients_facture)
        ))
    else:
        query = query.filter(*conditions)



    query = query.order_by(VAffaire.id.desc()).limit(search_limit).all()
    return Utils.serialize_many(query)


@view_config(route_name='types_affaires', request_method='GET', renderer='json')
@view_config(route_name='types_affaires_s', request_method='GET', renderer='json')
def types_affaires_view(request):
    """
    Return all types affaires
    """
    types_affaires = request.dbsession.query(AffaireType).filter(
        AffaireType.ordre != None
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

    # Check authorization
    if not Utils.has_permission(request, permission):
        raise exc.HTTPForbidden()

    model = Affaire()
    model = Utils.set_model_record(model, request.params)

    request.dbsession.add(model)
    # Récupèrer l'id de la nouvelle affaire
    request.dbsession.flush()

    # Créer le chemin du dossier de l'affaire
    model.chemin = os.path.join(request.registry.settings['affaires_directory'], str(model.id))

    # Copier le dossier __template pour une nouvelle affaire
    # copy_tree(request.registry.settings['affaireTemplateDir'], model.chemin)
    os.mkdir(model.chemin)
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
    date_time = datetime.now().strftime("%Y%m%d%H%M%S")
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
