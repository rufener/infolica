# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from infolica.exceptions.custom_error import CustomError
from infolica.models.constant import Constant
from infolica.models.models import SuiviMandat
from infolica.scripts.utils import Utils


@view_config(route_name='suivi_mandats', request_method='GET', renderer='json')
@view_config(route_name='suivi_mandats_s', request_method='GET', renderer='json')
def suivi_mandats_view(request):
    """
    Return all suivi_mandats
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    query = request.dbsession.query(SuiviMandat).all()
    return Utils.serialize_many(query)


@view_config(route_name='suivi_mandat_by_id', request_method='GET', renderer='json')
def suivi_mandats_by_id_view(request):
    """
    Return suivi_mandats by id
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    id = request.id = request.matchdict['id']
    query = request.dbsession.query(SuiviMandat).filter(
        SuiviMandat.id == id).first()
    return Utils.serialize_one(query)


@view_config(route_name='affaire_suivi_mandats_by_affaire_id', request_method='GET', renderer='json')
def affaire_suivi_mandats_by_affaire_id_view(request):
    """
    Return suivi_mandats by affaire_id
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    affaire_id = request.id = request.matchdict['id']
    query = request.dbsession.query(SuiviMandat).filter(
        SuiviMandat.affaire_id == affaire_id).first()

    if query is None:
        return None

    return Utils.serialize_one(query)


@view_config(route_name='suivi_mandats', request_method='POST', renderer='json')
@view_config(route_name='suivi_mandats_s', request_method='POST', renderer='json')
def suivi_mandats_new_view(request):
    """
    Add new suivi_mandats
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_suivi_edition']):
        raise exc.HTTPForbidden()

    record = SuiviMandat()
    record = Utils.set_model_record(record, request.params)

    request.dbsession.add(record)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(SuiviMandat.__tablename__))


@view_config(route_name='suivi_mandats', request_method='PUT', renderer='json')
@view_config(route_name='suivi_mandats_s', request_method='PUT', renderer='json')
def suivi_mandats_update_view(request):
    """
    Update suivi_mandats
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_suivi_edition']):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    id = request.params['id'] if 'id' in request.params else None

    # Get controle mutation record
    record = request.dbsession.query(SuiviMandat).filter(
        SuiviMandat.id == id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(SuiviMandat.__tablename__, id))

    record = Utils.set_model_record(record, request.params)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(SuiviMandat.__tablename__))


@view_config(route_name='suivi_mandats', request_method='DELETE', renderer='json')
@view_config(route_name='suivi_mandats_s', request_method='DELETE', renderer='json')
def suivi_mandats_delete_view(request):
    """
    Delete suivi_mandats
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_suivi_edition']):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    id = request.params['id'] if 'id' in request.params else None

    # Get controle mutation record
    record = request.dbsession.query(SuiviMandat).filter(
        SuiviMandat.id == id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(SuiviMandat.__tablename__, id))

    request.dbsession.delete(record)

    return Utils.get_data_save_response(Constant.SUCCESS_DELETE.format(SuiviMandat.__tablename__))
