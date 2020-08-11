# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc
from pyramid.response import Response
from pyramid.security import remember

from sqlalchemy import func

from infolica.models.models import Operateur
from infolica.scripts.ldap_query import LDAPQuery
from infolica.scripts.utils import Utils

import json

import logging
log = logging.getLogger(__name__)


@view_config(route_name='login', request_method='POST', renderer='json')
@view_config(route_name='login_s', request_method='POST', renderer='json')
def login_view(request):
    """
    Login
    """
    response = None

    login = None
    password = None

    if 'login' in request.params:
        login = request.params['login']

    if 'password' in request.params:
        password = request.params['password']

    # Check if user exists in DB
    query = request.dbsession.query(Operateur)
    log.info('Attempt to log with: {}'.format(login))
    operateur = query.filter(func.lower(
        Operateur.login) == func.lower(login)).first()

    if not operateur:
        return exc.HTTPNotFound('Username {} was not found'.format(login))

    try:
        resp_json = LDAPQuery.do_login(request, login, password)

    except Exception as error:
        log.error(str(error))
        return {'error': 'true', 'code': 403, 'message': str(error)}

    if resp_json and 'dn' in resp_json:
        headers = remember(request, resp_json['dn'])

        if operateur:
            operateur_json = Utils.serialize_one(operateur)
            """
            operateur_json['role_id'] = Utils.get_role_id_by_name(request, resp_json['role_name'])
            operateur_json['role_name'] = resp_json['role_name']
            operateur_json['fonctions'] = Utils.get_fonctions_roles_by_id(request, operateur_json['role_id'])
            operateur_json['fonctions'] = [x["nom"] for x in operateur_json['fonctions']]"""

            operateur_json = json.dumps(operateur_json) if operateur else ''

            response = Response(operateur_json, content_type='application/json; charset=UTF-8', headers=headers)

    return response


@view_config(route_name='logout', request_method='GET', renderer='json')
def logout_view(request):
    """
    Logout
    """
    response = None
    try:
        response = LDAPQuery.do_logout(request)

    except Exception as error:
        log.error(str(error))
        return {'error': 'true', 'code': 403, 'message': str(error)}

    return response
