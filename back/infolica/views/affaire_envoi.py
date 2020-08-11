# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from infolica.exceptions.custom_error import CustomError
from infolica.models.constant import Constant
from infolica.models.models import Envoi, EnvoiType, VEnvois
from infolica.scripts.utils import Utils

###########################################################
# ENVOIS AFFAIRE
###########################################################


@view_config(route_name='envois_types', request_method='GET', renderer='json')
@view_config(route_name='envois_types_s', request_method='GET', renderer='json')
def envois_types_view(request):
    """
    GET envois_type
    """

    records = request.dbsession.query(EnvoiType).all()
    return Utils.serialize_many(records)


@view_config(route_name='affaire_envois_by_affaire_id', request_method='GET', renderer='json')
def affaire_envois_view(request):
    """
    GET envois affaire
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    affaire_id = request.matchdict['id']

    records = request.dbsession.query(VEnvois).filter(
        VEnvois.affaire_id == affaire_id
    ).all()

    return Utils.serialize_many(records)


@view_config(route_name='envois', request_method='POST', renderer='json')
@view_config(route_name='envois_s', request_method='POST', renderer='json')
def envois_new_view(request):
    """
    POST envois
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_envois_edition']):
        raise exc.HTTPForbidden()

    model = Envoi()
    model = Utils.set_model_record(model, request.params)

    request.dbsession.add(model)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Envoi.__tablename__))


@view_config(route_name='envois', request_method='PUT', renderer='json')
@view_config(route_name='envois_s', request_method='PUT', renderer='json')
def envois_update_view(request):
    """
    UPDATE envoi
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_envois_edition']):
        raise exc.HTTPForbidden()

    record_id = request.params['id'] if 'id' in request.params else None
    record = request.dbsession.query(Envoi).filter(
        Envoi.id == record_id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(Envoi.__tablename__, record_id))

    record = Utils.set_model_record(record, request.params)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Envoi.__tablename__))


@view_config(route_name='envois_by_id', request_method='DELETE', renderer='json')
def envois_delete_view(request):
    """
    DELETE envois
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_envois_edition']):
        raise exc.HTTPForbidden()

    record_id = request.matchdict['id']

    record = request.dbsession.query(Envoi).filter(
        Envoi.id == record_id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(Envoi.__tablename__, record_id))

    request.dbsession.delete(record)

    return Utils.get_data_save_response(Constant.SUCCESS_DELETE.format(Envoi.__tablename__))
