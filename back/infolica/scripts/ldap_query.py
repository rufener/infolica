# -*- coding: utf-8 -*--
from pyramid.exceptions import ConfigurationError
from pyramid_ldap3 import get_ldap_connector
from pyramid.response import Response
from pyramid.security import forget

import json
import logging

LOG = logging.getLogger(__name__)


class LDAPQuery(object):

    @classmethod
    def do_login(cls, request, login, password):

        # Check if user exists in LDAP
        try:
            connector = get_ldap_connector(request)
        except ConfigurationError as error:
            LOG.error('Connector is not well configured. Error is : {}'.format(error))
        data = connector.authenticate(login, password)

        if data is not None:
            dn = data[0]

            if dn == 'null':
                raise Exception('Invalid credentials')

            resp_json = {}

            resp_json['role_name'] = cls.get_user_group_by_dn(request, dn)
            resp_json['dn'] = dn

            return resp_json

        else:
            raise Exception('LDAP authentication failed')

    @classmethod
    def do_logout(cls, request):
        headers = forget(request)
        response = Response('{"error": "false", "code": 200, "message": "User logged out"}', headers=headers)
        # response.headerlist.extend(headers)
        return response

    @classmethod
    def get_connected_user(cls, request):
        user_id = request.authenticated_userid

        connector = get_ldap_connector(request)

        with connector.manager.connection() as conn:
            ret = conn.search(
                search_scope=request.registry.settings['ldap_login_query_scope'],
                attributes=request.registry.settings['ldap_login_query_attributes'].replace(
                    ', ', ','
                ).replace(
                    ' , ', ','
                ).replace(
                    ' ,', ','
                ).split(','),
                search_base=request.registry.settings['ldap_login_query_base_dn'],
                search_filter=request.registry.settings['ldap_search_user_filter']
            )
            result, ret = conn.get_response(ret)

        if result is None:
            result = []
        else:
            result = [r['attributes'] for r in result
                      if 'dn' in r and r['dn'] == user_id]
            result = result[0] if result and len(result) > 0 else None

            if result is not None:
                result = json.loads(json.dumps(dict(result)))

        return cls.format_json_attributes(result) if result else {}

    @classmethod
    def get_user_group_by_dn(cls, request, dn):
        connector = get_ldap_connector(request)
        result = connector.user_groups(dn)
        group_to_avoid = request.registry.settings['infolica_group_to_avoid']

        if result is not None:
            groups = [
                cls.format_json_attributes(
                    json.loads(
                        json.dumps(dict(r[1]))
                    )
                ) for r in result if r and len(r) > 1]

            if groups and len(groups) > 0:
                cn_attribute = request.registry.settings['ldap_group_attribute_id']

                for group in groups:
                    if group[cn_attribute].startswith(request.registry.settings['infolica_groups_prefix']) \
                            and group_to_avoid not in group[cn_attribute]:
                        return group[cn_attribute]
        return None

    @classmethod
    def format_json_attributes(cls, json_obj):
        for key in json_obj:
            if isinstance(json_obj[key], list) and len(json_obj[key]) > 0:
                json_obj[key] = json_obj[key][0]

        return json_obj

    @classmethod
    def get_infolica_users(cls, request):
        users = []

        connector = get_ldap_connector(request)

        with connector.manager.connection() as conn:
            ret = conn.search(
                search_scope=request.registry.settings['ldap_login_query_scope'],
                attributes=request.registry.settings['ldap_login_query_attributes'].replace(', ', ',').replace(
                    ' , ', ',').replace(' ,', ',').split(','),
                search_base=request.registry.settings['ldap_login_query_base_dn'],
                search_filter=request.registry.settings['ldap_search_user_filter']
            )
            result, ret = conn.get_response(ret)

        if result is not None:
            for r in result:

                if 'dn' in r:
                    user_json = cls.format_json_attributes(json.loads(json.dumps(dict(r['attributes']))))
                    user_json['dn'] = r['dn']
                    users.append(user_json)

        return users if users else {}
