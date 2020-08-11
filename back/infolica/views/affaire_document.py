# -*- coding: utf-8 -*--
from pyramid.view import view_config
from pyramid.response import FileResponse
import pyramid.httpexceptions as exc

from infolica.exceptions.custom_error import CustomError
from infolica.models.constant import Constant
from infolica.models.models import Document, DocumentType, VDocumentsAffaires
from infolica.scripts.utils import Utils

import os
import shutil
from datetime import datetime


###########################################################
# DOCUMENTS (LISTE) AFFAIRE
###########################################################

@view_config(route_name='affaire_dossier_by_affaire_id', request_method='GET', renderer='json')
def affaire_dossier_view(request):
    """
    GET documents folder
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    affaire_dossier = request.registry.settings["affaires_directory"]
    affaire_id = request.matchdict['id']
    return os.path.join(affaire_dossier, affaire_id)


@view_config(route_name='affaire_documents_by_affaire_id', request_method='GET', renderer='json')
def affaire_documents_view(request):
    """
    GET documents affaire
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    affaire_id = request.matchdict['id']
    query = request.dbsession.query(VDocumentsAffaires).filter(VDocumentsAffaires.affaire_id == affaire_id).all()
    documents = Utils.serialize_many(query)

    for doc in documents:
        affaire_id = doc['affaire_id']
        filename = doc['nom']
        filepath = os.path.join(request.registry.settings['affaires_directory'], str(affaire_id), filename)
        doc['creation'] = datetime.fromtimestamp(os.path.getctime(filepath)).strftime("%d.%m.%Y")

    return documents


@view_config(route_name='types_documents', request_method='GET', renderer='json')
@view_config(route_name='types_documents_s', request_method='GET', renderer='json')
def types_documents_view(request):
    """
    Return all documents types
    """
    query = request.dbsession.query(DocumentType).all()
    return Utils.serialize_many(query)


@view_config(route_name='upload_affaire_document', request_method='POST', renderer='json')
def upload_affaire_document_view(request):
    """
    Upload document
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_edition']):
        raise exc.HTTPForbidden()

    affaire_id = request.params['affaire_id'] if 'affaire_id' in request.params else None

    # Create affaire folder if does not exist
    affaire_folder = os.path.join(request.registry.settings['affaires_directory'], affaire_id)
    Utils.create_affaire_folder(affaire_folder)
    fileslist = [request.POST[x] for x in request.POST if x.startswith('affaire_doc_files')]

    for f in fileslist:
        filename = f.filename
        input_file = f.file
        file_path = os.path.join(affaire_folder, filename)
        with open(file_path, 'wb') as output_file:
            shutil.copyfileobj(input_file, output_file)

        # Get document instance
        model = Utils.set_model_record(Document(), request.params)

        setattr(model, 'nom', filename)
        setattr(model, 'chemin', os.path.join(affaire_id, filename))

        request.dbsession.add(model)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Document.__tablename__))


@view_config(route_name='download_affaire_document', request_method='GET')
@view_config(route_name='download_affaire_document_s', request_method='GET')
def download_affaire_document_view(request):
    """
    Download document
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_edition']):
        raise exc.HTTPForbidden()

    affaires_directory = request.registry.settings['affaires_directory']
    affaire_id = request.params['affaire_id']
    filename = request.params['filename']

    if affaire_id:
        file_path = os.path.join(affaires_directory, affaire_id, filename)
        base_file_name = os.path.basename(file_path)

    import urllib
    response = FileResponse(file_path, request=request, cache_max_age=86400)
    headers = response.headers
    headers['Content-Type'] = 'application/download'
    headers['Accept-Ranges'] = 'bite'
    headers['Content-Disposition'] = 'attachment;filename=' + urllib.parse.quote(base_file_name)
    return response


@view_config(route_name='delete_affaire_document', request_method='DELETE', renderer='json')
def delete_affaire_document_view(request):
    """
    Delete document
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_edition']):
        raise exc.HTTPForbidden()

    # Get params
    affaires_directory = request.registry.settings['affaires_directory']
    id_doc = request.params['id']
    affaire_id = request.params['affaire_id']
    filename = request.params['nom']
    file_path = os.path.join(affaires_directory, affaire_id, filename)

    # Delete file from folder
    os.remove(file_path)

    # Delete file from DB
    record = request.dbsession.query(Document).filter(
        Document.id == id_doc).first()

    # If result is empty
    if not record:
        raise CustomError(CustomError.RECORD_WITH_ID_NOT_FOUND.format(
            Document.__tablename__, id_doc))

    request.dbsession.delete(record)

    return Utils.get_data_save_response(Constant.SUCCESS_DELETE.format(Document.__tablename__))
