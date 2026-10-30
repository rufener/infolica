# -*- coding: utf-8 -*--
from pyramid.view import view_config
from pyramid.response import FileResponse
import pyramid.httpexceptions as exc

from infolica.scripts.utils import Utils
from infolica.models.models import Affaire
from infolica.scripts.authentication import check_connected
import os

from datetime import datetime
import hmac
import urllib.parse
import uuid


###########################################################
# DOCUMENTS (LISTE) AFFAIRE
###########################################################


@view_config(route_name="affaire_dossier_by_affaire_id", request_method="GET", renderer="json")
def affaire_dossier_view(request):
    """
    GET documents folder
    """
    # Check connected
    if not check_connected(request):
        raise exc.HTTPForbidden()

    affaire_dossier = request.registry.settings["affaires_directory"]
    affaire_dossier_full_path = request.registry.settings["affaires_directory_full_path"]
    affaire_id = request.matchdict["id"]
    affaire_chemin = request.dbsession.query(Affaire).filter(Affaire.id == affaire_id).first().chemin

    chemin = "/!\   Le chemin n'est pas enregistré dans la base de données   /!\\"
    if not affaire_chemin is None:
        chemin = "/!\   Le chemin enregistré dans la base de données n'existe pas   /!\\"
        if os.path.exists(os.path.join(affaire_dossier, affaire_chemin)):
            chemin = os.path.normcase(os.path.join(affaire_dossier_full_path, affaire_chemin))

    return chemin


@view_config(route_name="affaire_documents_by_affaire_id", request_method="GET", renderer="json")
def affaire_documents_view(request):
    """
    GET documents affaire
    """
    # Check connected
    if not check_connected(request):
        raise exc.HTTPForbidden()

    affaire_id = request.params["affaire_id"] if "affaire_id" in request.params else None
    affaire_chemin = request.dbsession.query(Affaire).filter(Affaire.id == affaire_id).first().chemin

    documents = []
    if not affaire_chemin:
        return documents

    affaire_path = os.path.join(request.registry.settings["affaires_directory"], affaire_chemin).replace("\\", "/")
    for root, dirs, files in os.walk(affaire_path, topdown=False):
        for name in files:
            if name.startswith(".") or name.startswith("~"):
                continue
            file_i = {}
            file_i["relpath"] = os.path.relpath(root, affaire_path).replace("\\", "/")
            file_i["filename"] = name
            file_i["creation_sort"] = os.path.getctime(os.path.join(root, name))
            file_i["modification_sort"] = os.path.getmtime(os.path.join(root, name))
            file_i["creation"] = datetime.fromtimestamp(file_i["creation_sort"]).strftime("%d.%m.%Y")
            file_i["modification"] = datetime.fromtimestamp(file_i["modification_sort"]).strftime("%d.%m.%Y")
            documents.append(file_i)

    return documents


@view_config(route_name="download_affaire_document", request_method="GET")
@view_config(route_name="download_affaire_document_s", request_method="GET")
def download_affaire_document_view(request):
    """
    Download document
    """
    # Check connected
    if not check_connected(request, [*[request.registry.settings["service_mo"].replace(" ", "")], *request.registry.settings["preavis_services_externes"].replace(" ", "").split(",")]):
        raise exc.HTTPForbidden()

    affaires_directory = request.registry.settings["affaires_directory"]
    affaire_id = request.params["affaire_id"]
    relpath = request.params["relpath"]
    filename = request.params["filename"]
    affaire_chemin = request.dbsession.query(Affaire).filter(Affaire.id == affaire_id).first().chemin

    file_path = os.path.normcase(os.path.join(affaires_directory, affaire_chemin, relpath, filename))
    folder_path = os.path.exists(os.path.dirname(file_path))

    if not folder_path:
        Utils.create_affaire_folder(request, folder_path)

    response = FileResponse(file_path, request=request, cache_max_age=86400)
    headers = response.headers
    headers["Content-Type"] = "application/download"
    headers["Accept-Ranges"] = "bite"
    headers["Content-Disposition"] = "attachment;filename=" + urllib.parse.quote(filename)
    return response


###########################################################
# Open route for other services to get particular documents
###########################################################


@view_config(route_name="externe_document", request_method="GET")
def download_affaire_document_from_external_view(request):
    """
    Download document for SPCH
    """

    if not "affaire_id" in request.params:
        raise exc.HTTPInternalServerError("Primary key affaire_id is missing.")

    affaire_id = request.params["affaire_id"]

    affaire = request.dbsession.query(Affaire).filter(Affaire.id == affaire_id).first()
    token = request.params["uuid"] if "uuid" in request.params else None

    # Check token: refuse if affaire does not exist, has no uuid, or token is missing/invalid
    # (same response in every case to avoid revealing which affaires exist)
    try:
        token = str(uuid.UUID(token))
    except (TypeError, ValueError):
        token = None

    if affaire is None or affaire.uuid is None or token is None or not hmac.compare_digest(token, str(affaire.uuid)):
        raise exc.HTTPForbidden()

    if affaire.chemin is None:
        raise exc.HTTPNotFound("Specified path does not exist.")

    affaires_directory = request.registry.settings["affaires_directory"]
    affaire_path = os.path.join(affaires_directory, affaire.chemin)
    relpath = request.params["relpath"] if "relpath" in request.params else ""
    filename = os.path.basename(request.params["filename"] if "filename" in request.params else "")

    file_path = os.path.normcase(os.path.join(affaire_path, relpath, filename))

    # The file must stay inside the affaire folder, itself inside affaires_directory
    if not Utils.is_path_inside(affaires_directory, affaire_path) or not Utils.is_path_inside(affaire_path, file_path):
        raise exc.HTTPBadRequest("Specified path is not allowed.")

    if not os.path.isfile(file_path):
        raise exc.HTTPNotFound("Specified path does not exist.")

    response = FileResponse(file_path, request=request, cache_max_age=0)
    headers = response.headers
    headers["Content-Type"] = "application/download"
    headers["Accept-Ranges"] = "bytes"
    headers["Content-Disposition"] = "attachment;filename=" + urllib.parse.quote(filename)
    return response
