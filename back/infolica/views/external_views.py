# -*- coding: utf-8 -*--
from pyramid.view import view_config
from pyramid.response import FileResponse
import pyramid.httpexceptions as exc

from infolica.models.models import AccessibiliteAffaire, AccessibiliteService, Affaire
from infolica.scripts.authentication import check_connected
from datetime import datetime
from pathlib import Path
import urllib


## Open URLs for external services
@view_config(route_name="external_document", request_method="GET")
def download_document_from_external_service_view(request):
    """
    Download document for external service
    """

    # check if parameters are correctly setted
    if not "affaire_id" in request.params:
        raise exc.HTTPInternalServerError("Argument affaire_id is missing.")

    if not "filename" in request.params:
        raise exc.HTTPInternalServerError("Argument filename is missing.")

    affaire_id = int(request.params["affaire_id"])

    # Check token
    token = request.params["token"] if "token" in request.params else None
    access_affaire = request.dbsession.query(AccessibiliteAffaire).filter(AccessibiliteAffaire.affaire_id == affaire_id).first()
    if not str(token) == str(access_affaire.token):
        raise exc.HTTPForbidden()

    document = (
        request.dbsession.query(Affaire.id, Affaire.chemin, AccessibiliteAffaire.token, AccessibiliteAffaire.token_set, AccessibiliteService.interval, AccessibiliteService.relpath)  # 0  # 1  # 2  # 3  # 4  # 5
        .join(AccessibiliteAffaire, AccessibiliteAffaire.affaire_id == Affaire.id)
        .join(AccessibiliteService, AccessibiliteService.id == AccessibiliteAffaire.service_id)
        .filter(Affaire.id == affaire_id, AccessibiliteAffaire.token == token, AccessibiliteAffaire.token_set + AccessibiliteService.interval > datetime.today())
        .first()
    )

    if document == None:
        raise exc.HTTPInternalServerError("No reference found for this ressource.")

    affaires_directory = request.registry.settings["affaires_directory"]
    filename = request.params["filename"]

    file_path = Path(affaires_directory) / document[1] / document[5] / filename

    if not file_path.exists():
        raise exc.HTTPBadRequest("Path specified does not exist.")

    response = FileResponse(file_path, request=request, cache_max_age=86400)
    headers = response.headers
    headers["Content-Type"] = "application/download"
    headers["Accept-Ranges"] = "bite"
    headers["Content-Disposition"] = "attachment;filename=" + urllib.parse.quote(filename)
    return response
