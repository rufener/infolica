# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from infolica.exceptions.custom_error import CustomError
from infolica.models.constant import Constant
from infolica.models.models import NumeroRelation, VNumerosRelations
from infolica.models.models import VNumerosAffaires
from infolica.scripts.utils import Utils
from infolica.scripts.authentication import check_connected
from sqlalchemy import and_
import json


@view_config(route_name='numeros_relations', request_method='GET', renderer='json')
@view_config(route_name='numeros_relations_s', request_method='GET', renderer='json')
def numeros_relations_view(request):
    """
    Return all numeros_relations
    """
    # Check connected
    if not check_connected(request):
        raise exc.HTTPForbidden()

    query = request.dbsession.query(VNumerosRelations).all()
    return Utils.serialize_many(query)


@view_config(route_name='numeros_relation_by_affaire_id', request_method='GET', renderer='json')
def numeros_relation_by_affaire_id_view(request):
    """
    Return Numeros_relations
    """
    # Check connected
    if not check_connected(request):
        raise exc.HTTPForbidden()

    affaire_id = request.matchdict['id']

    # filter by conditions
    query = request.dbsession.query(VNumerosRelations).filter(
        VNumerosRelations.affaire_id == affaire_id).all()

    return Utils.serialize_many(query)


# """ Return all numeros_relations based on numero_base_id having project or valid numbers defined on it"""
# @view_config(route_name='numeros_relations_by_numeroBase', request_method='POST', renderer='json')
# @view_config(route_name='numeros_relations_by_numeroBase_s', request_method='POST', renderer='json')
# def numeros_relations_by_numeroBase_view(request):
#     # Check connected
#     if not check_connected(request):
#         raise exc.HTTPForbidden()

#     # Récupérer les indices des états projet et vigueur de la config
#     settings = request.registry.settings
#     numero_etat_projet_id = int(settings['numero_projet_id'])
#     numero_etat_vigueur_id = int(settings['numero_vigueur_id'])

#     # Récupérer la liste des numéros de base de l'affaire
#     numeros_base_id_list = request.params['numeros_base_id_list'] if 'numeros_base_id_list' in request.params else None
#     numeros_base_id_list = json.loads(numeros_base_id_list)

#     query = request.dbsession.query(models.VNumerosRelations).filter(
#         and_(
#             models.VNumerosRelations.numero_base_id.in_(numeros_base_id_list),
#             models.VNumerosRelations.numero_associe_etat_id.in_([numero_etat_projet_id, numero_etat_vigueur_id])
#         )).all()
#     return Utils.serialize_many(query)


@view_config(route_name='numeros_relations', request_method='POST', renderer='json')
@view_config(route_name='numeros_relations_s', request_method='POST', renderer='json')
def numeros_relations_new_view(request, params=None):
    """
    Add new numeros_relations
    """
    if params is None:
        params = request.params

    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()

    # check that relation does not exist yet
    conditions = []
    conditions.append(NumeroRelation.numero_id_base == params['numero_id_base'])
    conditions.append(NumeroRelation.numero_id_associe == params['numero_id_associe'])
    conditions.append(NumeroRelation.relation_type_id == params['relation_type_id'])
    conditions.append(NumeroRelation.affaire_id == params['affaire_id'])
    rel = request.dbsession.query(NumeroRelation).filter(*conditions).first()
    if not rel is None:
        return None
    
    # Get numeros_relations instance
    model = Utils.set_model_record(NumeroRelation(), params)

    request.dbsession.add(model)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(NumeroRelation.__tablename__))


@view_config(route_name='numeros_relations', request_method='PUT', renderer='json')
@view_config(route_name='numeros_relations_s', request_method='PUT', renderer='json')
def numeros_relations_update_view(request):
    """
    Update numeros_relations
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()
    
    model = request.dbsession.query(NumeroRelation)

    # get instance
    if "id" in request.params:
        numrel_id = request.params["id"]
        model = model.filter(NumeroRelation.id == numrel_id)
    else:
        num_base_id = request.params["numero_id_base"]
        num_associe_id = request.params["numero_id_associe"]
        affaire_old_id = request.params["affaire_old_id"]

        model = model.filter(and_(
            NumeroRelation.numero_id_base == num_base_id,
            NumeroRelation.numero_id_associe == num_associe_id,
            NumeroRelation.affaire_id == affaire_old_id,
        ))

    model = model.first()
    
    # update instance
    if model != None and "affaire_new_id" in request.params:
        model.affaire_id = request.params["affaire_new_id"] if "affaire_new_id" in request.params else None

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(NumeroRelation.__tablename__))


@view_config(route_name='numeros_relations', request_method='DELETE', renderer='json')
@view_config(route_name='numeros_relations_s', request_method='DELETE', renderer='json')
def numeros_relations_delete_view(request):
    """
    Delete numeros_relations
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()

    model = None
    numero_relation_id = None
    if "numero_relation_id" in request.params:
        numero_relation_id = request.params["numero_relation_id"]
        model = request.dbsession.query(NumeroRelation).filter(NumeroRelation.id == numero_relation_id).first()
    elif "numero_base_id" in request.params and "affaire_id" in request.params:
        numero_base_id = int(request.params["numero_base_id"])
        affaire_id = int(request.params["affaire_id"])
        numero_relation_id = "numero_base_id=" + request.params["numero_base_id"] + " & affaire_id=" + request.params["affaire_id"]
        model = request.dbsession.query(NumeroRelation).filter(and_(
            NumeroRelation.numero_id_base == numero_base_id,
            NumeroRelation.affaire_id == affaire_id
        )).first()
    else:
        raise CustomError.INCOMPLETE_REQUEST

    if not model:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(NumeroRelation.__tablename__, numero_relation_id))

    request.dbsession.delete(model)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(NumeroRelation.__tablename__))


@view_config(route_name='balance_partielle', request_method='POST', renderer='json')
def balance_partielle_view(request):
    """
    Get balance partielle
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()

    liste_numeros_id = json.loads(request.params['liste_numeros_id']) if 'liste_numeros_id' in request.params else None
    affaire_id = request.params['affaire_id'] if 'affaire_id' in request.params else None

    nr_req = request.dbsession.query(
        NumeroRelation
    ).filter(
        NumeroRelation.affaire_id == affaire_id
    )

    balance_partielle = []
    liste_numeros_parcourus = []
    c = 0

    while c < len(liste_numeros_id) and set(liste_numeros_parcourus).issubset(set(liste_numeros_id)):
        actual_number_id = liste_numeros_id[c]
        liste_numeros_parcourus.append(actual_number_id)

        related_nums_bases = nr_req.filter(
            NumeroRelation.numero_id_associe == actual_number_id
        ).all()

        related_nums_associes = nr_req.filter(
            NumeroRelation.numero_id_base == actual_number_id,
        ).all()

        for related_num in related_nums_bases:
            if related_num.numero_id_base not in liste_numeros_id and not related_num.numero_id_base in [1, 2]:
                liste_numeros_id.append(related_num.numero_id_base)
        
        for related_num in related_nums_associes:
            if related_num.numero_id_associe not in liste_numeros_id and not related_num.numero_id_associe in [1, 2]:
                liste_numeros_id.append(related_num.numero_id_associe)

        c += 1


    balance_partielle = request.dbsession.query(
        VNumerosAffaires
    ).filter(
        VNumerosAffaires.affaire_id == affaire_id,
        VNumerosAffaires.numero_id.in_(liste_numeros_id)
    ).all()

    return Utils.serialize_many(balance_partielle)
