# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from infolica.exceptions.custom_error import CustomError
from infolica.models.models import Affaire
from infolica.scripts.utils import Utils

import os
import json
from docx.api import Document


@view_config(route_name='balance_by_affaire_id', request_method='GET', renderer='json')
def balance_view(request):
    """
    Return balance ef affaire
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()
    
    affaire_id = request.matchdict["id"]

    # Get affaire path and search file
    query = request.dbsession.query(Affaire).filter(Affaire.id == affaire_id).first()
    path = query.chemin

    for filename in os.listdir(path):
        if filename.startswith and (filename.endswith(".doc") or filename.endswith(".docx")):
            break
    
    input_file = os.path.join(path, filename)
    
    # Open balance file and get table of balance
    doc = Document(input_file)
    table = None
    for table in doc.tables:
        if "ancien" in table.rows[0].cells[0].text:
            break
    
    lastBF = []
    balance = []
    for i, row in enumerate(table.rows[1:]):

        text = list(cell.text for cell in row.cells)
        
        if i == 0:
            lastBF = text
            continue
        
        for j, text_i in enumerate(text):
            if j >= 2 and text_i.isnumeric() and not text[0] == "":
                balance.append({
                        "new": int(lastBF[j]) if lastBF[j].isnumeric() else lastBF[j],
                        "old": int(text[0]) if text[0].isnumeric() else text[0]
                    })
    
    return json.dumps(balance)
