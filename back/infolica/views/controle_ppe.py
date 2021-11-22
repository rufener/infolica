# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from infolica.exceptions.custom_error import CustomError
from infolica.models import Constant
from infolica.models.models import ControlePPE, Operateur
from infolica.scripts.utils import Utils
from infolica.scripts.authentication import check_connected


@view_config(route_name='controles_ppe', request_method='GET', renderer='json')
@view_config(route_name='controles_ppe_s', request_method='GET', renderer='json')
def controles_ppe_view(request):
    """
    Return all controles_ppe
    """
    # Check connected
    if not check_connected(request):
        raise exc.HTTPForbidden()

    query = request.dbsession.query(ControlePPE).all()
    return Utils.serialize_many(query)


@view_config(route_name='controle_ppe_by_id', request_method='GET', renderer='json')
def controles_ppe_by_id_view(request):
    """
    Return controles_ppe by id
    """
    # Check connected
    if not check_connected(request):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    id = request.id = request.matchdict['id']
    query = request.dbsession.query(ControlePPE).filter(
        ControlePPE.id == id).first()
    return Utils.serialize_one(query)


@view_config(route_name='controle_ppe_by_affaire_id', request_method='GET', renderer='json')
def controles_ppe_by_affaire_id_view(request):
    """
    Return controles_ppe by affaire_id
    """
    # Check connected
    if not check_connected(request):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    affaire_id = request.id = request.matchdict['id']
    query = request.dbsession.query(ControlePPE).filter(
        ControlePPE.affaire_id == affaire_id).all()

    if query is None:
        return None

    ctrls = Utils.serialize_many(query)

    # search operateurs
    if len(ctrls) > 0:
        for ctrl in ctrls:
            operateur_id = ctrl['operateur_id']

            if operateur_id is not None:
                operateur = request.dbsession.query(
                    Operateur
                ).filter(
                    Operateur.id == operateur_id
                ).first()

                ctrl['operateur_prenom_nom'] = ' '.join([operateur.prenom, operateur.nom])
            else:
                ctrl['operateur_prenom_nom'] = None

    return ctrls

@view_config(route_name='controles_ppe', request_method='POST', renderer='json')
@view_config(route_name='controles_ppe_s', request_method='POST', renderer='json')
def controles_ppe_new_view(request):
    """
    Add new controles_ppe
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_edition']):
        raise exc.HTTPForbidden()

    Utils.addNewRecord(request, ControlePPE)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(ControlePPE.__tablename__))


@view_config(route_name='controles_ppe', request_method='PUT', renderer='json')
@view_config(route_name='controles_ppe_s', request_method='PUT', renderer='json')
def controles_ppe_update_view(request):
    """
    Update controles_ppe
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_edition']):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    id = request.params['id'] if 'id' in request.params else None

    # Get controle mutation record
    record = request.dbsession.query(ControlePPE).filter(
        ControlePPE.id == id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(ControlePPE.__tablename__, id))

    record = Utils.set_model_record(record, request.params)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(ControlePPE.__tablename__))


@view_config(route_name='controles_ppe', request_method='DELETE', renderer='json')
@view_config(route_name='controles_ppe_s', request_method='DELETE', renderer='json')
def controles_ppe_delete_view(request):
    """
    Delete controles_ppe
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_edition']):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    id = request.params['id'] if 'id' in request.params else None

    # Get controle mutation record
    record = request.dbsession.query(ControlePPE).filter(
        ControlePPE.id == id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(ControlePPE.__tablename__, id))

    request.dbsession.delete(record)

    return Utils.get_data_save_response(Constant.SUCCESS_DELETE.format(ControlePPE.__tablename__))
