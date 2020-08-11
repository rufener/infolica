# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from infolica.exceptions.custom_error import CustomError
from infolica.models.constant import Constant
from infolica.models.models import Preavis, PreavisType, VAffairesPreavis
from infolica.scripts.utils import Utils

###########################################################
# PREAVIS AFFAIRE
###########################################################


@view_config(route_name='preavis_type', request_method='GET', renderer='json')
@view_config(route_name='preavis_type_s', request_method='GET', renderer='json')
def preavis_type_view(request):
    """
    GET preavis type
    """
    records = request.dbsession.query(PreavisType).all()
    return Utils.serialize_many(records)


@view_config(route_name='affaire_preavis_by_affaire_id', request_method='GET', renderer='json')
def affaire_preavis_view(request):
    """
    GET preavis affaire
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    affaire_id = request.matchdict['id']

    records = request.dbsession.query(VAffairesPreavis).filter(
        VAffairesPreavis.affaire_id == affaire_id
        ).all()

    return Utils.serialize_many(records)


@view_config(route_name='preavis', request_method='POST', renderer='json')
@view_config(route_name='preavis_s', request_method='POST', renderer='json')
def preavis_new_view(request):
    """
    POST preavis affaire
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_preavis_edition']):
        raise exc.HTTPForbidden()

    model = Preavis()
    model = Utils.set_model_record(model, request.params)

    request.dbsession.add(model)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Preavis.__tablename__))


@view_config(route_name='preavis', request_method='PUT', renderer='json')
@view_config(route_name='preavis_s', request_method='PUT', renderer='json')
def preavis_update_view(request):
    """
    UPDATE preavis affaire
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_preavis_edition']):
        raise exc.HTTPForbidden()

    preavis_id = request.params['id'] if 'id' in request.params else None

    record = request.dbsession.query(Preavis).filter(
        Preavis.id == preavis_id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(Preavis.__tablename__, preavis_id))

    record = Utils.set_model_record(record, request.params)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Preavis.__tablename__))


@view_config(route_name='preavis_by_id', request_method='DELETE', renderer='json')
def preavis_delete_view(request):
    """
    DELETE preavis affaire
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_preavis_edition']):
        raise exc.HTTPForbidden()

    preavis_id = request.matchdict['id']

    record = request.dbsession.query(Preavis).filter(
        Preavis.id == preavis_id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(Preavis.__tablename__, preavis_id))

    request.dbsession.delete(record)

    return Utils.get_data_save_response(Constant.SUCCESS_DELETE.format(Preavis.__tablename__))


# # Remarques Préavis

# """ GET affaire preavis remarques"""
# @view_config(route_name='preavis_by_affaire_id', request_method='GET', renderer='json')
# def affaire_preavis_remarques_view(request):
#     affaire_id = request.matchdict['id']
#         records = request.dbsession.query(models.VAffairesPreavis)\
#             .filter(models.VAffairesPreavis.affaire_id == affaire_id).all()

#         return Utils.serialize_many(records)

#     except Exception as e:
#         log.error(e)
#         return exc.HTTPBadRequest(e)


# """ POST preavis affaire"""
# @view_config(route_name='preavis', request_method='POST', renderer='json')
# @view_config(route_name='preavis_s', request_method='POST', renderer='json')
# def preavis_new_view(request):

#     model = models.Preavis()
#     model = Utils.set_model_record(model, request.params)
#     request.dbsession.add(model)
#     return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(models.Preavis.__tablename__))

#     except Exception as e:
#         log.error(e)
#         return exc.HTTPBadRequest(e)


# """ UPDATE preavis affaire"""
# @view_config(route_name='preavis', request_method='PUT', renderer='json')
# @view_config(route_name='preavis_s', request_method='PUT', renderer='json')
# def preavis_update_view(request):
#     preavis_id = request.params['id'] if 'id' in request.params else None
#     record = request.dbsession.query(models.Preavis).filter(
#         models.Preavis.id == preavis_id).first()

#     if not record:
#         raise CustomError(
#             CustomError.RECORD_WITH_ID_NOT_FOUND.format(models.Preavis.__tablename__, preavis_id))

#     record = Utils.set_model_record(record, request.params)
#     return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(models.Preavis.__tablename__))
#     except Exception as e:
#         log.error(e)
#         return exc.HTTPBadRequest(e)


# """ DELETE preavis affaire"""
# @view_config(route_name='preavis_by_id', request_method='DELETE', renderer='json')
# def preavis_delete_view(request):
#     preavis_id = request.matchdict['id']
#     record = request.dbsession.query(models.Preavis).filter(
#         models.Preavis.id == preavis_id).first()
#     if not record:
#         raise CustomError(
#             CustomError.RECORD_WITH_ID_NOT_FOUND.format(models.Preavis.__tablename__, preavis_id))
#      request.dbsession.delete(record)
#      return Utils.get_data_save_response(Constant.SUCCESS_DELETE.format(models.Preavis.__tablename__))
#     except Exception as e:
#         log.error(e)
#         return exc.HTTPBadRequest(e)
