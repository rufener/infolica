# -*- coding: utf-8 -*--
from math import ceil
from pyramid.view import view_config
import pyramid.httpexceptions as exc
from pyramid.response import Response

from sqlalchemy.dialects.postgresql import aggregate_order_by

from infolica.exceptions.custom_error import CustomError
from infolica.models.constant import Constant
from infolica.models.models import Affaire, AffaireEtape, PreavisDecision, VAffaire, Operateur, Service
from infolica.models.models import PreavisRemarque, PreavisGlossaire
from infolica.models.models import Preavis, PreavisType, VAffairesPreavis
from infolica.scripts.utils import Utils
from infolica.scripts.mail_templates import MailTemplates
from infolica.scripts.authentication import check_connected

from datetime import datetime
import time
import os
import shutil
import requests

from sqlalchemy import func, cast, Text, or_

###########################################################
# PREAVIS AFFAIRE
###########################################################


@view_config(route_name='preavis_type', request_method='GET', renderer='json')
@view_config(route_name='preavis_type_s', request_method='GET', renderer='json')
def preavis_type_view(request):
    """
    GET preavis type
    """
    records = request.dbsession.query(PreavisType).all()
    return Utils.serialize_many(records)


@view_config(route_name='affaire_preavis_by_affaire_id', request_method='GET', renderer='json')
def affaire_preavis_view(request):
    """
    GET preavis affaire
    """
    # Check connected
    if not check_connected(request):
        raise exc.HTTPForbidden()

    affaire_id = request.matchdict['id']

    records = request.dbsession.query(VAffairesPreavis).filter(
        VAffairesPreavis.affaire_id == affaire_id
    ).all()

    preavis = Utils.serialize_many(records)

    for p in preavis:
        p['unread_remarks'] = Utils.check_unread_preavis_remarks(request, affaire_id, service_id=p['service_id'])

    return preavis


@view_config(route_name='preavis', request_method='POST', renderer='json')
@view_config(route_name='preavis_s', request_method='POST', renderer='json')
def preavis_new_view(request):
    """
    POST preavis affaire
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_preavis_edition']):
        raise exc.HTTPForbidden()

    model = Preavis()
    model = Utils.set_model_record(model, request.params)

    # add preavis folder if not exists
    affaires_directory = request.registry.settings['affaires_directory']
    service = request.dbsession.query(Service).filter(Service.id == model.service_id).first()
    affaire = request.dbsession.query(Affaire).filter(Affaire.id == model.affaire_id).first()
    preavis_service_path = os.path.join(affaires_directory, affaire.chemin, service.relpath)
    if not os.path.exists(preavis_service_path):
        os.makedirs(preavis_service_path)

    request.dbsession.add(model)
    request.dbsession.flush()

    # if a remarque for conversation is written, save it in PreavisRemarque
    remarque_conversation = request.params['remarque_conversation'] if 'remarque_conversation' in request.params else None
    if remarque_conversation is not None:
        _params = {
            'preavis_id': model.id,
            'remarque': remarque_conversation,
            'operateur_id': model.operateur_sgrf_id,
            'date': datetime.strftime(datetime.now(), '%Y-%m-%d')
        }
        Utils.addNewRecord(request, PreavisRemarque, _params)

    # Send mail to external service for a new preavis demand
    MailTemplates.sendMailPreavisDemande(request, model.id, model.service_id, message=remarque_conversation)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Preavis.__tablename__))


@view_config(route_name='preavis', request_method='PUT', renderer='json')
@view_config(route_name='preavis_s', request_method='PUT', renderer='json')
def preavis_update_view(request):
    """
    UPDATE preavis affaire
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_preavis_edition']):
        raise exc.HTTPForbidden()

    preavis_id = request.params['id'] if 'id' in request.params else None
    logstep = request.params['logstep'] == 'true' if 'logstep' in request.params else False

    preavis = request.dbsession.query(Preavis).filter(
        Preavis.id == preavis_id).first()

    if not preavis:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(Preavis.__tablename__, preavis_id))

    preavis = Utils.set_model_record(preavis, request.params)

    if logstep is True:
        service = request.dbsession.query(Service).filter(Service.id == preavis.service_id).first().abreviation
        Utils.newAffaireEtape(
            request=request,
            affaire_id=preavis.affaire_id,
            etape_id=request.registry.settings['affaire_etape_preavis_id'],
            remarque=service + ' - Demande',
        )

        # Send mail to external service for a new preavis demand
        MailTemplates.sendMailPreavisDemande(request, preavis.id, preavis.service_id)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Preavis.__tablename__))


@view_config(route_name='preavis', request_method='DELETE', renderer='json')
@view_config(route_name='preavis_s', request_method='DELETE', renderer='json')
def preavis_delete_view(request):
    """
    DELETE preavis affaire
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_preavis_edition']):
        raise exc.HTTPForbidden()

    preavis_id = request.params['preavis_id'] if 'preavis_id' in request.params else None

    record = request.dbsession.query(Preavis).filter(
        Preavis.id == preavis_id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(Preavis.__tablename__, preavis_id))

    request.dbsession.delete(record)

    return Utils.get_data_save_response(Constant.SUCCESS_DELETE.format(Preavis.__tablename__))



# ====================================================================
#    ROUTES POUR LES SERVICES EXTERNES
# ====================================================================

def strongAuthentication(request, preavis_id=None):
    # Check connected
    if check_connected(request, [request.registry.settings['service_mo'].replace(' ', '')]):
        operateur = Utils.getOperateurFromUser(request)
        return operateur

    if not check_connected(request, request.registry.settings['preavis_services_externes'].replace(' ', '').split(',')):
        raise exc.HTTPForbidden()

    # get service from user
    operateur = Utils.getOperateurFromUser(request)
    if operateur.service_id is None:
        raise exc.HTTPForbidden(detail="Opérateur non autorisé à accéder à ce contenu")

    if preavis_id is None:
        raise exc.HTTPInternalServerError(detail="L'identidifiant du préavis est manquant")

    testPreavis = request.dbsession.query(Preavis).filter(
        Preavis.service_id == operateur.service_id
    ).first()

    if testPreavis is None:
        raise exc.HTTPForbidden(detail="Aucune demande de préavis pour ce service")

    return operateur



@view_config(route_name='service_externe_preavis', request_method='GET', renderer='json')
def service_externe_preavis_view(request):
    """
    GET preavis for service externe
    """
    # Check connected
    if not check_connected(request, request.registry.settings['preavis_services_externes'].replace(' ', '').split(',')):
        raise exc.HTTPForbidden()

    # get service from user
    operateur = Utils.getOperateurFromUser(request)

    if operateur.service_id is None:
        exc.HTTPForbidden(detail="Opérateur non autorisé à accéder à ce contenu")

    status = request.params['status'] if 'status' in request.params else None
    search = request.params['search'] if 'search' in request.params else None

    query = request.dbsession.query(
        Preavis.id,
        Preavis.date_demande,
        Preavis.date_reponse,
        Preavis.affaire_id,
        VAffaire.cadastre,
        VAffaire.nom.label('affaire_description'),
        Operateur.prenom.label('operateur_prenom'),
        Operateur.nom.label('operateur_nom'),
        VAffaire.urgent,
        VAffaire.urgent_echeance,
        VAffaire.etape_id
    ).join(
        VAffaire, Preavis.affaire_id == VAffaire.id
    ).join(
        Operateur, Preavis.operateur_service_id == Operateur.id, isouter=True
    ).filter(
        Preavis.service_id == operateur.service_id
    )

    if status is not None:
        if status == "open":
            query = query.filter(
                Preavis.date_reponse == None,
                Preavis.etape == 'externe',
                VAffaire.date_cloture == None
            )
        elif status == "closed":
            query = query.filter(Preavis.etape == 'interne')
    else:
        query = query.filter(
            VAffaire.date_envoi == None,
            VAffaire.date_cloture == None
        )

    if search is not None:
        search = search.split(' ')
        for s in search:
            query = query.filter(
                or_(
                    cast(VAffaire.id, Text).ilike("%" + s + "%"),
                    VAffaire.nom.ilike("%" + s + "%"),
                    VAffaire.cadastre.ilike("%" + s + "%")
                )
            )

    query = query.order_by(Preavis.date_reponse.desc()) if status == "closed" else query.order_by(Preavis.date_demande.desc())

    if status is not None and status == "closed":
        query = query.limit(request.registry.settings['search_limit'])

    records = query.all()

    results = []
    for rec in records:
        remarque = ''
        priorite_idx = 2
        priorite = 'Normal'
        if rec.urgent is True:
            priorite_idx = 1
            priorite = 'Haut'
            tmp = 'Affaire urgente!'
            if rec.urgent_echeance is not None:
                tmp += ' (délai SGRF: ' + datetime.strftime(rec.urgent_echeance, '%d.%m.%Y') + ')'
            remarque += '<li>' + tmp + '</li>'
        if rec.etape_id in [int(request.registry.settings['affaire_etape_client_id']), int(request.registry.settings['affaire_etape_devis_id'])]:
            priorite_idx = 3
            priorite = 'Faible'
            remarque += '<li>En attente chez le client</li>'

        results.append({
            'preavis_id': rec.id,
            'preavis_date_demande': datetime.strftime(rec.date_demande, "%d.%m.%Y"),
            'preavis_date_demande_int': time.mktime(rec.date_demande.timetuple()),
            'preavis_date_reponse': datetime.strftime(rec.date_reponse, "%d.%m.%Y") if rec.date_reponse is not None else None,
            'preavis_date_reponse_int': time.mktime(rec.date_reponse.timetuple()) if rec.date_reponse is not None else None,
            'preavis_affaire_id': rec.affaire_id,
            'affaire_cadastre': rec.cadastre,
            'affaire_description': rec.affaire_description,
            'preavis_attribution': ' '.join(filter(None, [rec.operateur_prenom, rec.operateur_nom])),
            'unread_remarks': Utils.check_unread_preavis_remarks(request, rec.affaire_id, service_id=operateur.service_id),
            'priorite_idx': priorite_idx,
            'priorite': priorite,
            'remarque': remarque
        })

        if status == 'open':
            results = sorted(results, key=lambda x: x['priorite_idx'], reverse=False)

    return results


@view_config(route_name='service_externe_affaire', request_method='GET', renderer='json')
def service_externe_affaire_view(request):
    """
    GET affaire for service externe
    """
    preavis_id = request.params['preavis_id'] if 'preavis_id' in request.params else None
    strongAuthentication(request, preavis_id)

    record = request.dbsession.query(
        VAffaire.id,
        VAffaire.nom,
        VAffaire.client_commande_type_id,
        VAffaire.client_commande_entreprise,
        VAffaire.client_commande_titre,
        VAffaire.client_commande_nom,
        VAffaire.client_commande_prenom,
        VAffaire.client_commande_complement,
        VAffaire.client_commande_adresse,
        VAffaire.client_commande_co,
        VAffaire.client_commande_npa,
        VAffaire.client_commande_localite,
        VAffaire.client_commande_tel_fixe,
        VAffaire.client_commande_tel_portable,
        VAffaire.client_commande_mail,
        VAffaire.type_affaire,
        VAffaire.cadastre,
        VAffaire.date_ouverture,
        VAffaire.localisation_e,
        VAffaire.localisation_n,
        Preavis.id,
        Preavis.date_demande,
        Preavis.date_reponse,
        Preavis.etape,
        Preavis.service_id,
        VAffaire.urgent,
        VAffaire.urgent_echeance,
        VAffaire.etape_id,
        VAffaire.date_envoi
    ).filter(
        Preavis.id == preavis_id,
        VAffaire.id == Preavis.affaire_id,
    ).first()

    client = "\n".join(filter(None, [
        record[3],
        record[7],
        " ".join(filter(None, [record[4], record[6],  record[5]])),
        record[8],
        " ".join(filter(None, [record[10], record[11]])),
        record[12],
        record[13],
        record[14]
    ]))

    remarque_warning = ''
    if record[25] is True and record[28] is None:
        tmp = 'Affaire urgente, à traiter en priorité'
        if record[26] is not None:
            tmp += ' (délai de traitement au SGRF: ' + datetime.strftime(record[26], '%d.%m.%Y') + ')'
        remarque_warning += '<li>' + tmp + '</li>'
    if record[27] in [int(request.registry.settings['affaire_etape_client_id']), int(request.registry.settings['affaire_etape_devis_id'])]:
        remarque_warning += '<li>L''affaire est en attente chez le client</li>'

    result = {
        'id': record[0],
        'nom': record[1],
        'client': client,
        'type_affaire': record[15],
        'cadastre': record[16],
        'date_ouverture': datetime.strftime(record[17], "%d.%m.%Y"),
        'coord_e': record[18],
        'coord_n': record[19],
        'preavis_id': record[20],
        'preavis_date_demande': datetime.strftime(record[21], "%d.%m.%Y"),
        'preavis_date_reponse': datetime.strftime(record[22], "%d.%m.%Y") if record[22] is not None else None,
        'preavis_etape': record[23],
        'preavis_service_id': record[24],
        'remarque_warning': remarque_warning
    }

    return result


@view_config(route_name='service_externe_documents', request_method='GET', renderer='json')
def service_externe_documents_view(request):
    """
    GET documents of preavis_id for service externe
    """
    affaire_id = request.params['affaire_id'] if 'affaire_id' in request.params else None
    operateur = strongAuthentication(request, affaire_id)

    affaire_chemin = request.dbsession.query(Affaire).filter(Affaire.id == affaire_id).first().chemin

    # get rel path of service
    service_relpath = request.dbsession.query(Service).filter(Service.id == operateur.service_id).first().relpath
    courriers_courriels_rel_path = request.registry.settings['courriers_courriels_rel_path']
    documents = []
    for rel_path in [service_relpath, courriers_courriels_rel_path]:

        affaire_rel_path = os.path.join(affaire_chemin, rel_path)

        affaire_path = os.path.join(request.registry.settings['affaires_directory'], affaire_rel_path)

        if not os.path.exists(affaire_path):
            break


        for root, _, files in os.walk(affaire_path, topdown=False):
            for name in files:
                if name.startswith(".") or name.startswith("~"):
                    continue
                file_i = {}
                file_i['filename'] = name
                file_i['rel_path'] = rel_path
                file_i['size'] = str(ceil(os.path.getsize(os.path.join(root, name))/1000)) + ' ko' # ko
                file_i['creation_sort'] = os.path.getctime(os.path.join(root, name))
                file_i['modification_sort'] = os.path.getmtime(os.path.join(root, name))
                file_i['creation'] = datetime.fromtimestamp(file_i['creation_sort']).strftime("%d.%m.%Y")
                file_i['modification'] = datetime.fromtimestamp(file_i['modification_sort']).strftime("%d.%m.%Y")
                documents.append(file_i)

    return documents


@view_config(route_name='service_externe_conversation', request_method='GET', renderer='json')
def service_externe_conversation_view(request):
    """
    GET conversation of preavis_id for service externe
    """
    preavis_id = request.params['preavis_id'] if 'preavis_id' in request.params else None
    strongAuthentication(request, preavis_id)

    results = []

    query = request.dbsession.query(
        Operateur.id,
        Operateur.nom,
        Operateur.prenom,
        PreavisRemarque.date,
        PreavisRemarque.remarque,
        PreavisRemarque.lu_operateur_id,
        PreavisRemarque.id,
    ).join(
        Operateur, PreavisRemarque.operateur_id == Operateur.id
    ).join(
        Preavis, PreavisRemarque.preavis_id == Preavis.id
    ).filter(
        Preavis.id == preavis_id
    ).order_by(PreavisRemarque.id.desc()).all()


    connectedUser = Utils.getOperateurFromUser(request)
    pr_remark_user_query = request.dbsession.query(Operateur)

    for res in query:
        pr_remark_user = pr_remark_user_query.filter(Operateur.id == res[0]).first()
        unread = (res[5] is None) and (not connectedUser.service_id == pr_remark_user.service_id)

        results.append({
            "operateur": ' '.join([res[2], res[1]]),
            "date": datetime.strftime(res[3], "%d.%m.%Y"),
            "message": res[4],
            "unread": unread,
            "preavis_remarque_id": res[6]
        })

    return results


@view_config(route_name='service_externe_conversation', request_method='POST', renderer='json')
def service_externe_conversation_new_view(request):
    """
    POST conversation of preavis_id for service externe
    """
    preavis_id = request.params['preavis_id'] if 'preavis_id' in request.params else None
    commentaire = request.params['commentaire'] if 'commentaire' in request.params else None
    operateur = strongAuthentication(request, preavis_id)

    preavis = request.dbsession.query(Preavis).filter(
        Preavis.id == preavis_id
    ).first()

    rp = PreavisRemarque()

    params = {
        'preavis_id': preavis.id,
        'remarque': commentaire,
        'operateur_id': operateur.id,
        'date': datetime.strftime(datetime.now(), "%Y-%m-%d")
    }

    model = Utils.set_model_record(rp, params)
    request.dbsession.add(model)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(PreavisRemarque.__tablename__))


@view_config(route_name='service_externe_conversation', request_method='PUT', renderer='json')
def service_externe_conversation_update_view(request):
    """
    PUT conversation of preavis_id for service externe
    """
    preavis_remarque_id = request.params['preavis_remarque_id'] if 'preavis_remarque_id' in request.params else None
    lu_operateur_id = request.params['lu_operateur_id'] if 'lu_operateur_id' in request.params else None
    preavis_remarque = request.dbsession.query(PreavisRemarque).filter(PreavisRemarque.id == preavis_remarque_id).first()

    preavis_remarque.lu_operateur_id = lu_operateur_id

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(PreavisRemarque.__tablename__))


@view_config(route_name='service_externe_liste_decisions', request_method='GET', renderer='json')
def service_externe_liste_decision_view(request):
    """
    GET list of decisions of preavis_id for service externe
    """
    preavis_id = request.params['preavis_id'] if 'preavis_id' in request.params else None
    strongAuthentication(request, preavis_id)

    result = request.dbsession.query(
        PreavisDecision.id,
        PreavisDecision.date,
        PreavisDecision.version,
        PreavisDecision.remarque_contexte,
        PreavisDecision.remarque_limite_fictive_gabarits,
        PreavisDecision.remarque_transfert_droit_batir,
        PreavisDecision.remarque_stationnement_art29,
        PreavisDecision.remarque_autre,
        PreavisType.nom.label('decision'),
        Operateur.prenom.label('operateur_prenom'),
        Operateur.nom.label('operateur_nom'),
        PreavisDecision.preavis_type_id
    ).join(
        PreavisType, PreavisType.id == PreavisDecision.preavis_type_id
    ).join(
        Operateur, Operateur.id == PreavisDecision.operateur_service_id
    ).filter(
        PreavisDecision.preavis_id == preavis_id,
        PreavisDecision.definitif == True
    ).order_by(PreavisDecision.id.asc()).all()

    liste_decisions = []
    for res in result:
        liste_decisions.append(
            {
                'preavisDecision_id': res.id,
                'date': datetime.strftime(res.date, "%d.%m.%Y"),
                'version': res.version,
                'remarque_contexte': res.remarque_contexte,
                'remarque_limite_fictive_gabarits': res.remarque_limite_fictive_gabarits,
                'remarque_transfert_droit_batir': res.remarque_transfert_droit_batir,
                'remarque_stationnement_art29': res.remarque_stationnement_art29,
                'remarque_autre': res.remarque_autre,
                'decision': res.decision,
                'operateur': ' '.join([res.operateur_prenom, res.operateur_nom]),
                'preavis_type_id': res.preavis_type_id
            }
        )

    return liste_decisions


@view_config(route_name='service_externe_decision', request_method='GET', renderer='json')
def service_externe_decision_view(request):
    """
    GET decision of preavis_id for service externe
    """
    preavis_id = request.params['preavis_id'] if 'preavis_id' in request.params else None

    strongAuthentication(request, preavis_id)

    res = request.dbsession.query(
        PreavisDecision.preavis_type_id,
        PreavisDecision.remarque_contexte,
        PreavisDecision.remarque_limite_fictive_gabarits,
        PreavisDecision.remarque_transfert_droit_batir,
        PreavisDecision.remarque_stationnement_art29,
        PreavisDecision.remarque_autre,
        PreavisDecision.date,
        Operateur.prenom.label('operateur_prenom'),
        Operateur.nom.label('operateur_nom'),
        PreavisDecision.id,
        PreavisDecision.version,
    ).join(
        Operateur, Operateur.id == PreavisDecision.operateur_service_id
    ).filter(
        PreavisDecision.preavis_id == preavis_id,
        PreavisDecision.definitif.isnot(True)
    ).first()

    if res is not None:
        result = {
            'preavis_type_id': res.preavis_type_id,
            'remarque_contexte': res.remarque_contexte,
            'remarque_limite_fictive_gabarits': res.remarque_limite_fictive_gabarits,
            'remarque_transfert_droit_batir': res.remarque_transfert_droit_batir,
            'remarque_stationnement_art29': res.remarque_stationnement_art29,
            'remarque_autre': res.remarque_autre,
            'date': datetime.strftime(res.date, "%d.%m.%Y"),
            "operateur": ' '.join([res.operateur_prenom, res.operateur_nom]),
            "definitif": False,
            "id": res.id,
            "version": res.version,
        }
    else:
       result = None

    return result


@view_config(route_name='service_externe_decision', request_method='POST', renderer='json')
def service_externe_decision_new_view(request):
    """
    POST decision of preavis_id for service externe
    """
    preavis_id = request.params['preavis_id'] if 'preavis_id' in request.params else None
    preavis_type_id = request.params['preavis_type_id'] if 'preavis_type_id' in request.params else None
    remarque_contexte = request.params['remarque_contexte'] if 'remarque_contexte' in request.params else None
    remarque_limite_fictive_gabarits = request.params['remarque_limite_fictive_gabarits'] if 'remarque_limite_fictive_gabarits' in request.params else None
    remarque_transfert_droit_batir = request.params['remarque_transfert_droit_batir'] if 'remarque_transfert_droit_batir' in request.params else None
    remarque_stationnement_art29 = request.params['remarque_stationnement_art29'] if 'remarque_stationnement_art29' in request.params else None
    remarque_autre = request.params['remarque_autre'] if 'remarque_autre' in request.params else None
    definitif = request.params['definitif'] == 'true' if 'definitif' in request.params else False
    operateur = strongAuthentication(request, preavis_id)

    rp = PreavisDecision()
    max_version = request.dbsession.query(func.max(PreavisDecision.version)).filter(PreavisDecision.preavis_id == preavis_id).scalar()
    max_version = 0 if max_version is None else max_version

    params = {
        'preavis_id': preavis_id,
        'preavis_type_id': preavis_type_id,
        'operateur_service_id': operateur.id,
        'remarque_contexte': remarque_contexte,
        'remarque_limite_fictive_gabarits': remarque_limite_fictive_gabarits,
        'remarque_transfert_droit_batir': remarque_transfert_droit_batir,
        'remarque_stationnement_art29': remarque_stationnement_art29,
        'remarque_autre': remarque_autre,
        'date': datetime.strftime(datetime.now(), "%Y-%m-%d"),
        'version': max_version + 1,
        'definitif': definitif
    }

    model = Utils.set_model_record(rp, params)

    preavis = request.dbsession.query(Preavis).filter(Preavis.id == preavis_id).first()
    preavis.operateur_service_id = operateur.id

    request.dbsession.add(model)

    # send mail to SGRF project managers
    if definitif is True:
        # update preavis etape and other infos
        preavis.etape = 'interne'
        preavis.date_reponse = datetime.strftime(datetime.now(), "%Y-%m-%d")
        preavis.preavis_type_id = preavis_type_id
        preavis.remarque = '\n\n'.join(filter(None, [remarque_contexte, remarque_limite_fictive_gabarits, remarque_transfert_droit_batir, remarque_stationnement_art29, remarque_autre]))

        MailTemplates.sendMailPreavisReponse(request, preavis_id)

        # log step
        service = request.dbsession.query(Service).filter(Service.id == preavis.service_id).first().abreviation
        Utils.newAffaireEtape(
            request=request,
            affaire_id=preavis.affaire_id,
            etape_id=request.registry.settings['affaire_etape_preavis_id'],
            remarque=service + ' - Retour',
            operateur_id=preavis.operateur_service_id,
        )

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(PreavisDecision.__tablename__))


@view_config(route_name='service_externe_decision', request_method='PUT', renderer='json')
def service_externe_decision_update_view(request):
    """
    PUT decision of preavis_id for service externe
    """
    preavis_decision_id = request.params['preavis_decision_id'] if 'preavis_decision_id' in request.params else None
    preavis_id = request.params['preavis_id'] if 'preavis_id' in request.params else None
    preavis_type_id = request.params['preavis_type_id'] if 'preavis_type_id' in request.params else None
    remarque_contexte = request.params['remarque_contexte'] if 'remarque_contexte' in request.params else None
    remarque_limite_fictive_gabarits = request.params['remarque_limite_fictive_gabarits'] if 'remarque_limite_fictive_gabarits' in request.params else None
    remarque_transfert_droit_batir = request.params['remarque_transfert_droit_batir'] if 'remarque_transfert_droit_batir' in request.params else None
    remarque_stationnement_art29 = request.params['remarque_stationnement_art29'] if 'remarque_stationnement_art29' in request.params else None
    remarque_autre = request.params['remarque_autre'] if 'remarque_autre' in request.params else None
    definitif = request.params['definitif'] == 'true' if 'definitif' in request.params else False
    operateur = strongAuthentication(request, preavis_id)

    result = request.dbsession.query(PreavisDecision).filter(PreavisDecision.id == preavis_decision_id).first()

    result.preavis_type_id = preavis_type_id
    result.operateur_id = operateur.id
    result.remarque_contexte = remarque_contexte
    result.remarque_limite_fictive_gabarits = remarque_limite_fictive_gabarits
    result.remarque_transfert_droit_batir = remarque_transfert_droit_batir
    result.remarque_stationnement_art29 = remarque_stationnement_art29
    result.remarque_autre = remarque_autre
    result.date = datetime.strftime(datetime.now(), "%Y-%m-%d")
    result.definitif = definitif

    preavis = request.dbsession.query(Preavis).filter(Preavis.id == preavis_id).first()
    preavis.operateur_service_id = operateur.id

    if definitif is True:
        # update preavis etape and other infos
        preavis.etape = 'interne'
        preavis.date_reponse = datetime.strftime(datetime.now(), "%Y-%m-%d")
        preavis.preavis_type_id = preavis_type_id
        preavis.remarque = '\n\n'.join(filter(None, [remarque_contexte, remarque_limite_fictive_gabarits, remarque_transfert_droit_batir, remarque_stationnement_art29, remarque_autre]))

        # send mail to SGRF project managers
        MailTemplates.sendMailPreavisReponse(request, preavis_id)

        # log step
        service = request.dbsession.query(Service).filter(Service.id == preavis.service_id).first().abreviation
        Utils.newAffaireEtape(
            request=request,
            affaire_id=preavis.affaire_id,
            etape_id=request.registry.settings['affaire_etape_preavis_id'],
            remarque=service + ' - Retour',
            operateur_id=preavis.operateur_service_id
        )

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(PreavisDecision.__tablename__))


@view_config(route_name='service_externe_preavis_attribution', request_method='POST', renderer='json')
def service_externe_preavis_attribution_update_view(request):
    """
    POST attribution of preavis_id for service externe
    """
    preavis_id = request.params['preavis_id'] if 'preavis_id' in request.params else None
    operateur = strongAuthentication(request, preavis_id)

    preavis = request.dbsession.query(Preavis).filter(Preavis.id == preavis_id).first()

    preavis.operateur_service_id = operateur.id

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Preavis.__tablename__))


@view_config(route_name='service_externe_save_documents', request_method='POST', renderer='json')
def service_externe_save_documents_new_view(request):
    """
    POST preavis documents in affaire_id for service externe
    """
    affaire_id = request.params['affaire_id'] if 'affaire_id' in request.params else None
    operateur = strongAuthentication(request, affaire_id)

    service = request.dbsession.query(Service).filter(
        Service.id == operateur.service_id
    ).first()

    output_path = os.path.join(
        request.registry.settings['affaires_directory'],
        affaire_id,
        service.relpath
    )

    file_i = 0
    while 'files[' + str(file_i) + ']' in request.params:
        file = request.params['files[' + str(file_i) + ']']

        filename = file.filename
        input_file = file.file

        file_path = os.path.join(output_path, filename)
        file_path_tentative = file_path
        if os.path.exists(file_path_tentative):
            c = 1
            file_path_tentative = file_path.rsplit('.', 1)[0] + '_' + str(c) + '.' + file_path.rsplit('.', 1)[1]
            while os.path.exists(file_path_tentative):
                c += 1
                file_path_tentative = file_path.rsplit('.', 1)[0] + '_' + str(c) + '.' + file_path.rsplit('.', 1)[1]

        file_path = file_path_tentative
        with open(file_path, 'wb') as output_file:
            shutil.copyfileobj(input_file, output_file)

        # increment file_i
        file_i += 1

    return exc.HTTPOk(detail="Les fichiers ont bien été enregistrés")


@view_config(route_name='service_externe_glossaire', request_method='GET', renderer='json')
def service_externe_glossaire_view(request):
    """
    GET glossaire of service externe
    """
    preavis_id = request.params['preavis_id'] if 'preavis_id' in request.params else None

    operateur = strongAuthentication(request, preavis_id)

    results = request.dbsession.query(
        PreavisGlossaire.chapitre,
        func.array_agg(aggregate_order_by(PreavisGlossaire.texte, PreavisGlossaire.ordre.asc())).label('textes')
    ).filter(
        PreavisGlossaire.service_id == operateur.service_id
    ).group_by(
        PreavisGlossaire.chapitre
    ).order_by(
        PreavisGlossaire.chapitre.asc(),
    ).all()

    glossaire = {}
    for res in results:
        glossaire[res[0]] = res[1]

    return glossaire


@view_config(route_name='preavis_print', request_method='POST')
def preavis_print_view(request):
    """
    GET PDF of specified preavis
    """
    preavis_id = request.params['preavis_id'] if 'preavis_id' in request.params else None

    data = request.dbsession.query(
        Preavis.affaire_id,
        Service.service,
        Preavis.date_demande,
        Preavis.date_reponse,
        PreavisType.nom.label('preavis_type_nom'),
        VAffaire.cadastre,
        Service.abreviation.label('abreviation'),
        VAffaire.nom.label('affaire_description'),
        Preavis.operateur_service_id,
        Service.telephone.label('service_telephone'),
        Service.mail.label('service_mail'),
    ).join(
        Service
    ).join(
        PreavisType, PreavisType.id == Preavis.preavis_type_id, isouter=True
    ).join(
        VAffaire, VAffaire.id == Preavis.affaire_id
    ).filter(
        Preavis.id == preavis_id
    ).first()

    operateur = None
    if data.operateur_service_id is not None:
        operateur = request.dbsession.query(Operateur).filter(Operateur.id == data.operateur_service_id).first()


    preavis_decisions = request.dbsession.query(
        PreavisDecision.id,
        PreavisDecision.date,
        PreavisDecision.version,
        PreavisDecision.remarque_contexte,
        PreavisDecision.remarque_limite_fictive_gabarits,
        PreavisDecision.remarque_transfert_droit_batir,
        PreavisDecision.remarque_stationnement_art29,
        PreavisDecision.remarque_autre,
        PreavisType.nom,
        Operateur.prenom.label('operateur_prenom'),
        Operateur.nom.label('operateur_nom'),
        PreavisDecision.preavis_type_id
    ).join(
        PreavisType, PreavisType.id == PreavisDecision.preavis_type_id
    ).join(
        Operateur, Operateur.id == PreavisDecision.operateur_service_id
    ).filter(
        PreavisDecision.preavis_id == preavis_id,
        PreavisDecision.definitif == True
    ).order_by(PreavisDecision.id.asc()).all()

    liste_decisions = []
    preavis_version_max = 1
    for res in preavis_decisions:
        preavis_version_max = res.version if res.version > preavis_version_max else preavis_version_max
        liste_decisions.append(
            {
                'preavisDecision_id': res.id,
                'date': datetime.strftime(res.date, "%d.%m.%Y"),
                'version': res.version,
                'remarque_contexte': res.remarque_contexte,
                'remarque_limite_fictive_gabarits': res.remarque_limite_fictive_gabarits,
                'remarque_transfert_droit_batir': res.remarque_transfert_droit_batir,
                'remarque_stationnement_art29': res.remarque_stationnement_art29,
                'remarque_autre': res.remarque_autre,
                'decision': res.nom,
                'operateur': ' '.join([res.operateur_prenom, res.operateur_nom]),
                'preavis_type_id': res.preavis_type_id
            }
        )



    now = datetime.now()
    d = {"now": now.strftime("%d.%m.%Y, %H:%M:%S")}

    html = "<html><head><meta charset='UTF-8'><style>"

    ppp = """
        .logo {{
            width: 3.68cm;
            image-resolution: 300dpi
        }}
        @page {{
            size: A4 portrait;
            margin: 2cm;
            counter-increment: page;
            @bottom-left {{
                content: "Impression du {now}";
                font-family: Calibri, Candara, Segoe, Segoe UI, Optima, Arial, sans-serif; font-size: 7pt;
            }}
            @bottom-center {{
                content: "Page " counter(page) " de " counter(pages);
                font-family: Calibri, Candara, Segoe, Segoe UI, Optima, Arial, sans-serif; font-size: 7pt;
                border-top: .25pt solid #666;
                width: 60%;
            }}
            @bottom-right {{
                content: "SERVICE DE LA GEOMATIQUE ET DU REGISTRE FONCIER";
                font-family: Calibri, Candara, Segoe, Segoe UI, Optima, Arial, sans-serif; font-size: 7pt;
            }}
        }}
        h1 {{ font-family: Calibri, Candara, Segoe, Segoe UI, Optima, Arial, sans-serif; font-size: 18pt; font-style: normal; font-variant: normal; font-weight: 700; line-height: 20pt; }}
        h2 {{ font-family: Calibri, Candara, Segoe, Segoe UI, Optima, Arial, sans-serif; font-size: 16pt; font-style: normal; font-variant: normal; font-weight: 700; line-height: 18pt; }}
        h3 {{ font-family: Calibri, Candara, Segoe, Segoe UI, Optima, Arial, sans-serif; font-size: 14pt; font-style: normal; font-variant: normal; font-weight: 700; line-height: 16pt; }}
        p {{ font-family: Calibri, Candara, Segoe, Segoe UI, Optima, Arial, sans-serif; font-size: 12pt; font-style: normal; font-variant: normal; font-weight: 400; line-height: 14pt; text-align: justify; }}
        .title {{
            width: 400px;
            font-weight: bold;
            font-size: 15pt;
            color: black;
            opacity: 0.8;
            padding-bottom: 15px;
        }}

        .subtitle {{
            font-weight: bold;
            color: black;
            opacity: 0.7;
            font-size: 12pt;
            padding-bottom: 10px;
        }}

        .subtitle::before {{
            content: '-';
            padding-right: 10px;
            padding-left: 5px;
        }}
        """

    html += ppp.format(**d)
    html += "</style></head>"

    html += "<body>"
    html += "<img class='logo' src='https://sitn.ne.ch/web/images/06ne.ch_RVB.png' alt='Logo'>"
    html += '<p style="font-size: 8pt; line-height: 8pt; margin-top: 0mm; padding-top: 1mm; margin-left: 0mm; padding-left: 0mm;"><b>DÉPARTEMENT DU DÉVELOPPEMENT<br> \
                    TERRITORIAL ET DE L\'ENVIRONNEMENT</b><br> \
                    SERVICE DE LA GÉOMATIQUE ET<br> \
                    DU REGISTRE FONCIER</p>'

    html += "<h1>Préavis du " + data.service + "</h1>"
    if data.service_telephone is not None or data.service_mail is not None:
        html += "<p>Contact: "

        contacts = []
        if data.service_telephone is not None:
            contacts.append(data.service_telephone)

        if data.service_mail is not None:
            contacts.append(
                "<a href=\"mailto:" + data.service_mail + "?subject=Préavis de l'affaire: " + str(data.affaire_id) + " du cadastre: " + data.cadastre + "\">" + data.service_mail + "</a>"
            )

        html += " / ".join(contacts) + "</p>"


    html += "<p>Affaire n° " + str(data.affaire_id) + "<br>" + "Cadastre: " + data.cadastre + "</p>"
    html += "<p>Description de l'affaire: " + data.affaire_description + "</p>"
    html += "<p>Date de la demande de préavis: " + str(data.date_demande.strftime("%d.%m.%Y")) + "</p>"
    html += "<br>"
    html += "<h2>Version n° {} (en vigueur)</h2>".format(preavis_version_max)
    html += "<p>Préavisé le {}".format(str(data.date_reponse.strftime("%d.%m.%Y")))
    if operateur is not None:
        html += " par: " + operateur.prenom + " " + operateur.nom
    html += "</p>"
    html += "<br>"
    html += "<p style='font-weight: bold; background-color: LightGray; font-size: 14pt; padding: 4pt'>Préavis: " + (data.preavis_type_nom if data.preavis_type_nom is not None else 'indéfini') + "</p>"
    html += "<br>"
    html += "<p><em>Détail:</em></p><p style='white-space: pre-line;'><em>" +\
        "<div class='title'>Contexte et situation</div>" +\
        "<div style='white-space: pre-line;'>" + (liste_decisions[-1]['remarque_contexte'] or '-') + "</div>" +\
        "<br><br><hr><hr><br>" +\
        "<div class='title'>Servitude(s) / mention(s)</div>" +\
        "<div class='subtitle'>Limite fictive de gabarits</div>" +\
        "<div style='white-space: pre-line;'>" + (liste_decisions[-1]['remarque_limite_fictive_gabarits'] or '-') + "</div>" +\
        "<br><br><br>" +\
        "<div class='subtitle'>Transfert de droits à bâtir</div>" +\
        "<div style='white-space: pre-line;'>" + (liste_decisions[-1]['remarque_transfert_droit_batir'] or '-') + "</div>" +\
        "<br><br><br>" +\
        "<div class='subtitle'>Place de stationnement (Article 26 RELConstr.)</div>" +\
        "<div style='white-space: pre-line;'>" + (liste_decisions[-1]['remarque_stationnement_art29'] or '-') + "</div>" +\
        "<br><br><br>" +\
        "<div class='subtitle'>Autres servitudes et mentions</div>" +\
        "<div style='white-space: pre-line;'>" + (liste_decisions[-1]['remarque_autre'] or '-') + "</div>" +\
        "</em></p>"

    if len(liste_decisions)>1:
        for c, decision in enumerate(liste_decisions[:-1]):

            html += "<div style='break-after:page'></div>" # SAUT DE PAGE
            if c == 0:
                html += "<h1>HISTORIQUE DES PREAVIS</h1>"
            html += "<h2>Version n° {} (remplacée par la version n° {})</h2>".format(decision['version'], preavis_version_max)
            html += "<p>Préavisé le {} par {}</p>".format(decision['date'], decision['operateur'])
            html += "<br>"
            html += "<p style='font-weight: bold; background-color: LightGray; font-size: 14pt; padding: 4pt'>Préavis: " + (decision['decision'] if decision['decision'] is not None else 'indéfini') + "</p>"
            html += "<br>"
            html += "<p><em>Détail:</em></p><p style='white-space: pre-line;'><em>" +\
                "<div class='title'>Contexte et situation</div>" +\
                "<div style='white-space: pre-line;'>" + (decision['remarque_contexte'] or '-') + "</div>" +\
                "<br><br><hr><hr><br>" +\
                "<div class='title'>Servitude(s) / mention(s)</div>" +\
                "<div class='subtitle'>Limite fictive de gabarits</div>" +\
                "<div style='white-space: pre-line;'>" + (decision['remarque_limite_fictive_gabarits'] or '-') + "</div>" +\
                "<br><br><br>" +\
                "<div class='subtitle'>Transfert de droits à bâtir</div>" +\
                "<div style='white-space: pre-line;'>" + (decision['remarque_transfert_droit_batir'] or '-') + "</div>" +\
                "<br><br><br>" +\
                "<div class='subtitle'>Place de stationnement (Article 26 RELConstr.)</div>" +\
                "<div style='white-space: pre-line;'>" + (decision['remarque_stationnement_art29'] or '-') + "</div>" +\
                "<br><br><br>" +\
                "<div class='subtitle'>Autres servitudes et mentions</div>" +\
                "<div style='white-space: pre-line;'>" + (decision['remarque_autre'] or '-') + "</div>" +\
                "</em></p>"




    html += "</body></html>"

    filename = "Préavis_" + str(data.abreviation) + "_Affaire_" + str(data.affaire_id) + ".pdf"

    html = html.encode('utf-8')

    result = requests.post(request.registry.settings['weasyprint_baseurl'] + filename, data=html)

    response = Response(result.content)
    params = response.content_type_params
    params['filename'] = filename
    response.content_type = 'application/pdf'
    response.content_type_params = params
    return response


@view_config(route_name='service_externe_affaire_preavis_tous', request_method='GET', renderer='json')
def service_externe_affaire_preavis_tous(request):
    """
    GET all preavis in one sepecified affaire
    """

    preavis_id = request.params['preavis_id'] if 'preavis_id' in request.params else None
    strongAuthentication(request, preavis_id)

    affaire_id = request.params['affaire_id'] if 'affaire_id' in request.params else None

    results = request.dbsession.query(
        Preavis.id,
        Preavis.affaire_id,
        Preavis.service_id,
        Service.abreviation,
        Preavis.preavis_type_id,
        PreavisType.nom,
        Preavis.operateur_sgrf_id,
        # Preavis.operateur_service_id,
        Preavis.date_demande,
        Preavis.date_reponse,
        Preavis.remarque,
        Preavis.etape,
    ).filter(
        Preavis.affaire_id == affaire_id
    ).join(
        Service, Service.id == Preavis.service_id
    ).join(
        PreavisType, PreavisType.id == Preavis.preavis_type_id
    ).order_by(
        Preavis.date_demande.asc(),
        Preavis.date_reponse.asc()
    ).all()

    data = []
    for res in results:
        data.append({
            "id": res[0],
            "affaire_id": res[1],
            "service_id": res[2],
            "service": res[3],
            "preavis_type_id": res[4],
            "preavis_type": res[5],
            "operateur_sgrf_id": res[6],
            # "operateur_service_id": res[],
            "date_demande": Utils.date_isoformat(res[7]),
            "date_reponse": Utils.date_isoformat(res[8]),
            "remarque": res[9].replace("\n\nnull", ""),
            "etape": res[10],
        })

    return data
