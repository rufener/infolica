# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from infolica.exceptions.custom_error import CustomError
from infolica.models import Constant
from infolica.models.models import ControleMutation, Operateur
from infolica.scripts.utils import Utils
from infolica.scripts.authentication import check_connected

@view_config(route_name='controles_mutations', request_method='GET', renderer='json')
@view_config(route_name='controles_mutations_s', request_method='GET', renderer='json')
def controles_mutations_view(request):
    """
    Return all controles_mutations
    """
    # Check connected
    if not check_connected(request):
        raise exc.HTTPForbidden()

    query = request.dbsession.query(ControleMutation).all()
    return Utils.serialize_many(query)


@view_config(route_name='controle_mutation_by_id', request_method='GET', renderer='json')
def controles_mutations_by_id_view(request):
    """
    Return controle_mutation by id
    """
    # Check connected
    if not check_connected(request):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    id = request.id = request.matchdict['id']
    query = request.dbsession.query(ControleMutation).filter(
        ControleMutation.id == id).first()
    return Utils.serialize_one(query)


@view_config(route_name='controle_mutation_by_affaire_id', request_method='GET', renderer='json')
def controles_mutations_by_affaire_id_view(request):
    """
    Return controle_mutation by affaire_id
    """
    # Check connected
    if not check_connected(request):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    affaire_id = request.id = request.matchdict['id']
    query = request.dbsession.query(ControleMutation).filter(
        ControleMutation.affaire_id == affaire_id).first()

    if query is None:
        return None

    ctrl = Utils.serialize_one(query)

    # get operateur
    operateur_id = ctrl['visa']

    if operateur_id is not None:
        operateur = request.dbsession.query(
            Operateur
        ).filter(
            Operateur.id == operateur_id
        ).first()

        ctrl['operateur_prenom_nom'] = ' '.join([operateur.prenom, operateur.nom])
    else:
        ctrl['operateur_prenom_nom'] = None

    return ctrl


@view_config(route_name='controles_mutations', request_method='POST', renderer='json')
@view_config(route_name='controles_mutations_s', request_method='POST', renderer='json')
def controles_mutations_new_view(request):
    """
    Add new controle_mutation
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_edition']):
        raise exc.HTTPForbidden()

    Utils.addNewRecord(request, ControleMutation)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(ControleMutation.__tablename__))


@view_config(route_name='controles_mutations', request_method='PUT', renderer='json')
@view_config(route_name='controles_mutations_s', request_method='PUT', renderer='json')
def controles_mutations_update_view(request):
    """
    Update controle_mutation
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_edition']):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    id = request.params['id'] if 'id' in request.params else None

    # Get controle mutation record
    record = request.dbsession.query(ControleMutation).filter(
        ControleMutation.id == id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(ControleMutation.__tablename__, id))

    record = Utils.set_model_record(record, request.params)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(ControleMutation.__tablename__))


@view_config(route_name='controles_mutations', request_method='DELETE', renderer='json')
@view_config(route_name='controles_mutations_s', request_method='DELETE', renderer='json')
def controles_mutations_delete_view(request):
    """
    Delete controle_mutation
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_edition']):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    id = request.params['id'] if 'id' in request.params else None

    # Get controle mutation record
    record = request.dbsession.query(ControleMutation).filter(
        ControleMutation.id == id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(ControleMutation.__tablename__, id))

    request.dbsession.delete(record)

    return Utils.get_data_save_response(Constant.SUCCESS_DELETE.format(ControleMutation.__tablename__))


@view_config(route_name='controle_mutation_geos', request_method='GET', renderer='json')
def controles_mutations_delete_view(request):
    """
    Trigger controle_mutation_geos
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_edition']):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    affaire_id = request.params['affaire_id'] if 'affaire_id' in request.params else None

    operateur = Utils.getOperateurFromUser(request)

    url = request.registry.settings['infolica_cron_url_trigger'] + 'controle_mutation_geos?' \
                'variables=mutation={}|initiale={}|mail={}'.format(affaire_id, operateur.initiales, operateur.mail)
    
    return {'url': url}
