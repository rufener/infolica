# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from infolica.models.models import Affaire, Service
from infolica.scripts.authentication import check_connected
from infolica.scripts.utils import Utils

import os
import json
from docxtpl import DocxTemplate, RichText


@view_config(route_name='save_document', request_method='POST', renderer='json')
def save_document_view(request):
    """
    Save file (preavis)
    """
    # Check connected
    if not check_connected(request):
        raise exc.HTTPForbidden()

    settings = request.registry.settings
    affaires_directory = settings['affaires_directory']

    # Get request params
    affaire_id = str(request.params['affaire_id'])
    template = request.params['template']
    values = request.params['values']
    service_id = request.params['service_id'] if 'service_id' in request.params else None
    relPath = request.params['relpath'].strip('/').strip('\\') if 'relpath' in request.params else ""
    filename = request.params['filename'] if 'filename' in request.params else None

    # Set output file name
    output_file_name = filename if filename is not None else template
    if service_id:
        service = request.dbsession.query(Service).filter(Service.id == service_id).first()
        if service is None:
            raise exc.HTTPBadRequest("Le service {} n'existe pas".format(service_id))
        output_file_name += "_" + service.abreviation
        relPath = service.relpath.strip('/').strip('\\')

    # Only allow plain names for the template and the output file
    template_path = Utils.get_template_path(request, template)
    Utils.check_file_name(output_file_name)

    affaire = request.dbsession.query(Affaire).filter(Affaire.id == affaire_id).first()
    if affaire is None:
        raise exc.HTTPNotFound("L'affaire {} n'existe pas".format(affaire_id))

    affaire_relpath = affaire.chemin

    if affaire_relpath is None:
        affaire_relpath = affaire_id

    affaire_path = os.path.normcase(os.path.join(affaires_directory, affaire_relpath))

    filename = output_file_name + '.docx'
    file_path = os.path.normcase(os.path.join(affaire_path, relPath, filename))

    # The file must stay inside the affaire folder, itself inside affaires_directory
    if not Utils.is_path_inside(affaires_directory, affaire_path) or not Utils.is_path_inside(affaire_path, file_path):
        raise exc.HTTPBadRequest("Chemin invalide")

    if not os.path.exists(affaire_path):
        Utils.create_affaire_folder(request, affaire_path)
        # update affaire chemin
        affaire.chemin = affaire_relpath

    # Set context
    context = json.loads(values)
    for key in context.keys():
        context[key] = RichText(context[key])

    # Ouverture du document template
    doc = DocxTemplate(template_path)

    # Replace values by keywords and save
    doc.render(context)
    doc.save(file_path)

    return {'filename': filename, "folderpath": relPath}
