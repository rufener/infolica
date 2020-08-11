# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from infolica.exceptions.custom_error import CustomError
from infolica.models.constant import Constant
from infolica.models.models import Operateur, RemarqueAffaire
from infolica.scripts.utils import Utils

###########################################################
# REMARQUES AFFAIRE
###########################################################


@view_config(route_name='affaires_remarques_by_affaire_id', request_method='GET', renderer='json')
def affaires_remarques_view(request):
    """
    GET remarque affaire
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    affaire_id = request.matchdict['id']

    records = request.dbsession.query(RemarqueAffaire, Operateur)\
        .filter(RemarqueAffaire.affaire_id == affaire_id)\
        .filter(RemarqueAffaire.operateur_id == Operateur.id).all()

    ra_json = list()
    for ra, op in records:
        ra_json.append(Utils._params(id=ra.id, nom=op.nom, prenom=op.prenom,
                                     remarque=ra.remarque, date=ra.date.isoformat()))

    return ra_json


@view_config(route_name='remarques_affaires', request_method='POST', renderer='json')
@view_config(route_name='remarques_affaires_s', request_method='POST', renderer='json')
def affaires_remarques_new_view(request):
    """
    POST remarque affaire
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_remarque_edition']):
        raise exc.HTTPForbidden()

    model = RemarqueAffaire()
    model = Utils.set_model_record(model, request.params)

    request.dbsession.add(model)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(RemarqueAffaire.__tablename__))


@view_config(route_name='remarques_affaires', request_method='PUT', renderer='json')
@view_config(route_name='remarques_affaires_s', request_method='PUT', renderer='json')
def remarques_affaires_update_view(request):
    """
    PUT remarque affaire
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_remarque_edition']):
        raise exc.HTTPForbidden()

    remarque_affaire_id = request.params['id'] if 'id' in request.params else None

    record = request.dbsession.query(RemarqueAffaire).filter(
        RemarqueAffaire.id == remarque_affaire_id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(RemarqueAffaire.__tablename__, remarque_affaire_id))

    record = Utils.set_model_record(record, request.params)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(RemarqueAffaire.__tablename__))


@view_config(route_name='remarques_affaires_by_id', request_method='DELETE', renderer='json')
def remarques_affaires_delete_view(request):
    """
    DELETE remarque affaire
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_remarque_edition']):
        raise exc.HTTPForbidden()

    remarque_affaire_id = request.matchdict['id']

    record = request.dbsession.query(RemarqueAffaire).filter(
        RemarqueAffaire.id == remarque_affaire_id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(RemarqueAffaire.__tablename__, remarque_affaire_id))

    request.dbsession.delete(record)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(RemarqueAffaire.__tablename__))
