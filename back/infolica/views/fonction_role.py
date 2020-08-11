# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from infolica.scripts.utils import Utils
from infolica.scripts.ldap_query import LDAPQuery

import logging
log = logging.getLogger(__name__)

###########################################################
# Fonctions roles
###########################################################

""" Return all fonctions
@view_config(route_name='fonctions', request_method='GET', renderer='json')
@view_config(route_name='fonctions_s', request_method='GET', renderer='json')
def fonctions_view(request):
    query = request.dbsession.query(Fonction).all()
    return Utils.serialize_many(query)"""


""" Return all roles
@view_config(route_name='roles', request_method='GET', renderer='json')
@view_config(route_name='roles_s', request_method='GET', renderer='json')
def roles_view(request):
    query = request.dbsession.query(Role).all()
    return Utils.serialize_many(query)"""


""" Return fonctions roles by role id
@view_config(route_name='fonctions_roles_by_id', request_method='GET', renderer='json')
def fonctions_roles_by_id_view(request):
    id = request.matchdict['id']
    return Utils.get_fonctions_roles_by_id(request, id)"""


@view_config(route_name='fonctions_roles_current_user', request_method='GET', renderer='json')
def fonctions_roles_current_user_view(request):
    """
    Return fonctions of current user
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    operateur_json = {}
    role_name = LDAPQuery.get_user_group_by_dn(request, request.authenticated_userid)
    operateur_json['role_id'] = Utils.get_role_id_by_name(request, role_name)
    operateur_json['role_name'] = role_name
    operateur_json['fonctions'] = Utils.get_fonctions_roles_by_id(request, operateur_json['role_id'])
    operateur_json['fonctions'] = [x["nom"] for x in operateur_json['fonctions']]
    return operateur_json
