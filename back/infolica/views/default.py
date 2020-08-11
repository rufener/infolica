# -*- coding: utf-8 -*--
from pyramid.httpexceptions import HTTPForbidden, HTTPNoContent
from pyramid.view import notfound_view_config, view_config

from sqlalchemy import exc

from infolica.exceptions.custom_error import CustomError
from infolica.models.models import Client
from infolica.scripts.utils import Utils

import logging
log = logging.getLogger(__name__)


@view_config(route_name='test_client', request_method='POST', renderer='json')
def test_error(exc, request):
    """
    Test (temp endpoint)
    """
    query = request.dbsession.query(Client).first()
    query = Utils.set_model_record(query, request.params)
    return Utils.serialize_one(query)


@view_config(route_name='login', request_method='OPTIONS', renderer='json')
@view_config(route_name='login_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='logout', request_method='OPTIONS', renderer='json')
@view_config(route_name='affaires', request_method='OPTIONS', renderer='json')
@view_config(route_name='affaires_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='recherche_clients', request_method='OPTIONS', renderer='json')
@view_config(route_name='recherche_clients_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='recherche_affaires', request_method='OPTIONS', renderer='json')
@view_config(route_name='recherche_affaires_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='recherche_numeros', request_method='OPTIONS', renderer='json')
@view_config(route_name='recherche_numeros_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='clients', request_method='OPTIONS', renderer='json')
@view_config(route_name='clients_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='operateurs', request_method='OPTIONS', renderer='json')
@view_config(route_name='operateurs_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='factures', request_method='OPTIONS', renderer='json')
@view_config(route_name='factures_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='numero_by_id', request_method='OPTIONS', renderer='json')
@view_config(route_name='reference_numeros', request_method='OPTIONS', renderer='json')
@view_config(route_name='reference_numeros_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='preavis', request_method='OPTIONS', renderer='json')
@view_config(route_name='preavis_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='suivi_mandats', request_method='OPTIONS', renderer='json')
@view_config(route_name='suivi_mandats_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='controles_mutations', request_method='OPTIONS', renderer='json')
@view_config(route_name='controles_mutations_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='controles_ppe', request_method='OPTIONS', renderer='json')
@view_config(route_name='controles_ppe_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='numeros_differes', request_method='OPTIONS', renderer='json')
@view_config(route_name='numeros_differes_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='courrier_affaire', request_method='OPTIONS', renderer='json')
@view_config(route_name='courrier_affaire_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='delete_affaire_document', request_method='OPTIONS', renderer='json')
@view_config(route_name='numeros', request_method='OPTIONS', renderer='json')
@view_config(route_name='numeros_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='numeros_relations', request_method='OPTIONS', renderer='json')
@view_config(route_name='numeros_relations_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='affaire_numeros', request_method='OPTIONS', renderer='json')
@view_config(route_name='affaire_numeros_s', request_method='OPTIONS', renderer='json')
@view_config(route_name='client_moral_personnes', request_method='OPTIONS', renderer='json')
@view_config(route_name='client_moral_personnes_s', request_method='OPTIONS', renderer='json')
def options_response_view(request):
    """
    Common OPTION RESPONSE
    """
    return ''


@view_config(context=Exception, renderer='json')
def general_error(exc, request):
    """
    Common Exception return message
    """
    log.error(str(exc.orig) if hasattr(exc, 'orig') else str(exc))
    request.response.status = 500
    return {'error': 'true', 'code': 500, 'message': CustomError.GENERAL_EXCEPTION}


@view_config(context=exc.IntegrityError, renderer='json')
def integrity_error(exc, request):
    """
    Common IntegrityError return message
    """
    log.error(str(exc.orig) if hasattr(exc, 'orig') else str(exc))
    request.response.status = 500
    return {'error': 'true', 'code': 500, 'message': CustomError.GENERAL_EXCEPTION}


@view_config(context=exc.StatementError, renderer='json')
def statement_error(exc, request):
    """
    Common StatementError return message
    """
    log.error(str(exc.orig) if hasattr(exc, 'orig') else str(exc))
    request.response.status = 500
    return {'error': 'true', 'code': 500, 'message': CustomError.GENERAL_EXCEPTION}


@view_config(context=exc.ResourceClosedError, renderer='json')
def resource_closed_error(exc, request):
    """
    Common ResourceClosedError return message
    """
    log.error(str(exc.orig) if hasattr(exc, 'orig') else str(exc))
    request.response.status = 500
    return {'error': 'true', 'code': 500, 'message': CustomError.GENERAL_EXCEPTION}


@view_config(context=exc.InternalError, renderer='json')
def internal_error(exc, request):
    """
    Common InternalError return message
    """
    log.error(str(exc.orig) if hasattr(exc, 'orig') else str(exc))
    request.response.status = 500
    return {'error': 'true', 'code': 500, 'message': CustomError.GENERAL_EXCEPTION}


@view_config(context=exc.NoReferenceError, renderer='json')
def noreference_error(exc, request):
    """
    Common NoReferenceError return message
    """
    log.error(str(exc.orig) if hasattr(exc, 'orig') else str(exc))
    request.response.status = 500
    return {'error': 'true', 'code': 500, 'message': CustomError.GENERAL_EXCEPTION}


@view_config(context=exc.InvalidRequestError, renderer='json')
def invalidrequest_error(exc, request):
    """
    Common InvalidRequestError, return message
    """
    log.error(str(exc.orig) if hasattr(exc, 'orig') else str(exc))
    request.response.status = 500
    return {'error': 'true', 'code': 500, 'message': CustomError.GENERAL_EXCEPTION}


@view_config(context=exc.DBAPIError, renderer='json')
def dbaapi_error(exc, request):
    """
    Common DBAPIError return message
    """
    log.error(str(exc.orig) if hasattr(exc, 'orig') else str(exc))
    request.response.status = 500
    return {'error': 'true', 'code': 500, 'message': CustomError.GENERAL_EXCEPTION}


@view_config(context=exc.SQLAlchemyError, renderer='json')
def sqlalchemy_error(exc, request):
    """
    Common SQLAlchemyError return message
    """
    log.error(str(exc.orig) if hasattr(exc, 'orig') else str(exc))
    request.response.status = 500
    return {'error': 'true', 'code': 500, 'message': CustomError.GENERAL_EXCEPTION}


@view_config(context=HTTPForbidden, renderer='json')
def http_forbidden_error(exc, request):
    """
    Common HTTPForbidden return message
    """
    log.error(str(exc.orig) if hasattr(exc, 'orig') else str(exc))
    request.response.status = 403
    return {'error': 'true', 'code': 403, 'message': CustomError.NOT_AUTHORIZED_EXCEPTION}


@view_config(context=HTTPNoContent, renderer='json')
def http_no_content_error(exc, request):
    """
    Common HTTPNoContent return message
    """
    log.error(str(exc.orig) if hasattr(exc, 'orig') else str(exc))
    request.response.status = 204


@notfound_view_config(renderer="json")
def notfound(request):
    """
    Common notfound return message
    """
    msg = CustomError.NOT_FOUND_ERROR.format(request.url, request.method)
    log.error(msg)
    request.response.status = 404
    return {'error': 'true', 'code': 403, 'message': msg}
