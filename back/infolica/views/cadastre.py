# -*- coding: utf-8 -*--
from pyramid.view import view_config

from infolica.models.models import Cadastre
from infolica.scripts.utils import Utils

###########################################################
# Cadastre
###########################################################


@view_config(route_name='cadastres', request_method='GET', renderer='json')
@view_config(route_name='cadastres_s', request_method='GET', renderer='json')
def cadastre_view(request):
    """
    GET cadastre
    """
    # Check connected
    # if not Utils.check_connected(request):
    # raise exc.HTTPForbidden()

    records = request.dbsession.query(Cadastre).order_by(Cadastre.nom).all()
    cadastres = list()

    # Supprimer l'entrée "CADASTRE CANTONAL" de la liste
    for record_i in records:
        if not record_i.nom == "CADASTRE CANTONAL":
            cadastres.append(record_i)

    cadastres = Utils.serialize_many(cadastres)
    return cadastres
