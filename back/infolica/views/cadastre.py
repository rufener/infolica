from pyramid.view import view_config
#import pyramid.httpexceptions as exc
from .. import models
from ..scripts.utils import Utils


###########################################################
# Cadastre
###########################################################

""" GET cadastre"""
@view_config(route_name='cadastres', request_method='GET', renderer='json')
@view_config(route_name='cadastres_s', request_method='GET', renderer='json')
def cadastre_view(request):
    try:
        # Check connected
        #if not Utils.check_connected(request):
            #raise exc.HTTPForbidden()

        records = request.dbsession.query(models.Cadastre).order_by(models.Cadastre.nom).all()
        cadastres = Utils.serialize_many(records)

        # Supprimer l'entrée "CADASTRE CANTONAL" de la liste
        cadastres.pop(9)
        return cadastres

    except Exception as e:
        raise e

