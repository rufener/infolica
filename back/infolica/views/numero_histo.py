# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from infolica.models.models import VNumerosRelations
from infolica.scripts.utils import Utils

###########################################################
# NUMERO ETAT HISTO
###########################################################


@view_config(route_name='numero_base_relations_by_id', request_method='GET', renderer='json')
def numero_base_relations_view(request):
    """
    Get new numero_base_relations
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    numero_id = request.matchdict["id"]

    record = request.dbsession.query(VNumerosRelations).filter(VNumerosRelations.numero_associe_id == numero_id).all()

    if record:
        return Utils.serialize_many(record)
    else:
        return None


@view_config(route_name='numero_associe_relations_by_id', request_method='GET', renderer='json')
def numero_associe_relations_view(request):
    """
    Get new numero_associe_relations
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    numero_id = request.matchdict["id"]

    record = request.dbsession.query(VNumerosRelations).filter(VNumerosRelations.numero_base_id == numero_id).all()

    if record:
        return Utils.serialize_many(record)
    else:
        return None
