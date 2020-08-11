# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from sqlalchemy import and_

from infolica.models.constant import Constant
from infolica.models.models import AffaireNumero, Numero
from infolica.scripts.utils import Utils
from infolica.views.numero import affaire_numero_new_view

import json


@view_config(route_name='reference_numeros', request_method='POST', renderer='json')
@view_config(route_name='reference_numeros_s', request_method='POST', renderer='json')
def reference_numeros_new_view(request):
    """
    Add numéro muté in affaire
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()

    # Get affaire_id
    affaire_id = request.params['affaire_id'] if 'affaire_id' in request.params else None
    numeros_liste = json.loads(
        request.params['numeros_liste']) if 'numeros_liste' in request.params else None

    for numero_i in numeros_liste:
        # enregistrer le lien affaire-numéro
        params = Utils._params(
            affaire_id=affaire_id, numero_id=numero_i['numero_id'], actif=True, type_id=1)
        affaire_numero_new_view(request, params)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Numero.__tablename__))


@view_config(route_name='reference_numeros', request_method='DELETE', renderer='json')
@view_config(route_name='reference_numeros_s', request_method='DELETE', renderer='json')
def reference_numeros_delete_view(request):
    """
    Add numéro muté in affaire
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()

    # Get affaire_id and numero_id
    affaire_id = request.params['affaire_id'] if 'affaire_id' in request.params else None
    numero_id = request.params['numero_id'] if 'numero_id' in request.params else None

    # supprimer le lien affaire-numéro
    affNum = request.dbsession.query(AffaireNumero).filter(and_(
        AffaireNumero.affaire_id == affaire_id, AffaireNumero.numero_id == numero_id)).first()

    request.dbsession.delete(affNum)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Numero.__tablename__))
