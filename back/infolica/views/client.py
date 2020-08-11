from pyramid.view import view_config
import pyramid.httpexceptions as exc

from infolica.exceptions.custom_error import CustomError
from infolica.models import Constant
from infolica.models.models import Client, ClientType, ClientMoralPersonne
from infolica.scripts.utils import Utils

from datetime import datetime


@view_config(route_name='types_clients', request_method='GET', renderer='json')
@view_config(route_name='types_clients_s', request_method='GET', renderer='json')
def types_clients_view(request):
    """
    Return all types clients
    """
    query = request.dbsession.query(ClientType).all()
    return Utils.serialize_many(query)


@view_config(route_name='clients', request_method='GET', renderer='json')
@view_config(route_name='clients_s', request_method='GET', renderer='json')
def clients_view(request):
    """
    Return all clients
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    query = request.dbsession.query(Client).all()
    return Utils.serialize_many(query)


@view_config(route_name='client_by_id', request_method='GET', renderer='json')
def client_by_id_view(request):
    """
    Return client by id
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    id = request.matchdict['id']
    query = request.dbsession.query(Client).filter(
        Client.id == id).first()
    return Utils.serialize_one(query)


@view_config(route_name='recherche_clients', request_method='POST', renderer='json')
@view_config(route_name='recherche_clients_s', request_method='POST', renderer='json')
def clients_search_view(request):
    """
    Search clients
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    settings = request.registry.settings
    search_limit = int(settings['search_limit'])
    conditions = Utils.get_search_conditions(Client, request.params)

    # Check date_sortie is null
    conditions = [] if not conditions or len(
        conditions) == 0 else conditions

    conditions.append(Client.sortie == None)

    query = request.dbsession.query(Client).order_by(Client.nom, Client.prenom).filter(
        *conditions).limit(search_limit).all()
    return Utils.serialize_many(query)


@view_config(route_name='clients', request_method='POST', renderer='json')
@view_config(route_name='clients_s', request_method='POST', renderer='json')
def clients_new_view(request):
    """
    Add new client
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['client_edition']):
        raise exc.HTTPForbidden()

    # Get client instance
    model = Utils.set_model_record(Client(), request.params)

    request.dbsession.add(model)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Client.__tablename__))


@view_config(route_name='clients', request_method='PUT', renderer='json')
@view_config(route_name='clients_s', request_method='PUT', renderer='json')
def clients_update_view(request):
    """
    Update client
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['client_edition']):
        raise exc.HTTPForbidden()

    # Get client_id
    id_client = request.params['id'] if 'id' in request.params else None

    model = request.dbsession.query(Client).filter(
        Client.id == id_client).first()

    # If result is empty
    if not model:
        raise CustomError(CustomError.RECORD_WITH_ID_NOT_FOUND.format(
            Client.__tablename__, id_client))

    # Read params client
    model = Utils.set_model_record(model, request.params)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Client.__tablename__))


@view_config(route_name='clients', request_method='DELETE', renderer='json')
@view_config(route_name='clients_s', request_method='DELETE', renderer='json')
def clients_delete_view(request):
    """
    Delete client
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['client_edition']):
        raise exc.HTTPForbidden()

    # Get client_id
    id_client = request.params['id'] if 'id' in request.params else None

    model = request.dbsession.query(Client).filter(
        Client.id == id_client).first()

    # If result is empty
    if not model:
        raise CustomError(CustomError.RECORD_WITH_ID_NOT_FOUND.format(
            Client.__tablename__, id_client))

    model.sortie = datetime.utcnow()

    return Utils.get_data_save_response(Constant.SUCCESS_DELETE.format(Client.__tablename__))


# ClientMoralPersonnes
@view_config(route_name='client_moral_personnes_by_client_id', request_method='GET', renderer='json')
def types_client_moral_personnes_by_client_id_view(request):
    """
    Return all people in client_moral
    """
    client_id = request.matchdict['client_id'] if 'client_id' in request.matchdict else None

    query = request.dbsession.query(ClientMoralPersonne).filter(ClientMoralPersonne.client_id == client_id).all()
    return Utils.serialize_many(query)


@view_config(route_name='client_moral_personnes', request_method='POST', renderer='json')
@view_config(route_name='client_moral_personnes_s', request_method='POST', renderer='json')
def clients_moral_personne_new_view(request):
    """
    Add new contact in entreprise
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['client_edition']):
        raise exc.HTTPForbidden()

    # Get clientMoralPersonne instance
    model = Utils.set_model_record(ClientMoralPersonne(), request.params)

    request.dbsession.add(model)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(ClientMoralPersonne.__tablename__))


@view_config(route_name='client_moral_personnes', request_method='PUT', renderer='json')
@view_config(route_name='client_moral_personnes_s', request_method='PUT', renderer='json')
def clients_moral_personne_update_view(request):
    """
    Update contact in entreprise
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['client_edition']):
        raise exc.HTTPForbidden()

    client_moral_personne_id = request.params["id"] if "id" in request.params else None
    
    model = request.dbsession.query(ClientMoralPersonne).filter(
        ClientMoralPersonne.id == client_moral_personne_id).first()

    # If result is empty
    if not model:
        raise CustomError(CustomError.RECORD_WITH_ID_NOT_FOUND.format(
            ClientMoralPersonne.__tablename__, client_moral_personne_id))

    # Read params client
    model = Utils.set_model_record(model, request.params)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(ClientMoralPersonne.__tablename__))


@view_config(route_name='client_moral_personnes', request_method='DELETE', renderer='json')
@view_config(route_name='client_moral_personnes_s', request_method='DELETE', renderer='json')
def client_moral_personnes_delete_view(request):
    """
    Delete client_moral_personnes
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['client_edition']):
        raise exc.HTTPForbidden()

    # Get client_id
    client_moral_personne_id = request.params['id'] if 'id' in request.params else None

    model = request.dbsession.query(ClientMoralPersonne).filter(
        ClientMoralPersonne.id == client_moral_personne_id).first()

    # If result is empty
    if not model:
        raise CustomError(CustomError.RECORD_WITH_ID_NOT_FOUND.format(
            ClientMoralPersonne.__tablename__, client_moral_personne_id))

    request.dbsession.delete(model)

    return Utils.get_data_save_response(Constant.SUCCESS_DELETE.format(Client.__tablename__))