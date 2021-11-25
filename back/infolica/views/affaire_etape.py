# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from sqlalchemy import and_

from infolica.exceptions.custom_error import CustomError
from infolica.models.constant import Constant
from infolica.models.models import AffaireEtape, AffaireEtapeIndex, VEtapesAffaires, VAffaire
from infolica.models.models import EtapeMailer, Operateur, Affaire, Facture, Client
from infolica.scripts.utils import Utils
from infolica.scripts.mailer import send_mail
from infolica.scripts.authentication import check_connected
import os

###########################################################
# ETAPES AFFAIRE
###########################################################
@view_config(route_name='etapes_index', request_method='GET', renderer='json')
@view_config(route_name='etapes_index_s', request_method='GET', renderer='json')
def etapes_index_view(request):
    """
    GET etapes index
    """
    # Check connected
    if not check_connected(request):
        raise exc.HTTPForbidden()

    records = request.dbsession.query(AffaireEtapeIndex).filter(
        AffaireEtapeIndex.ordre != None
        ).order_by(AffaireEtapeIndex.ordre.asc()).all()
    return Utils.serialize_many(records)


@view_config(route_name='affaire_etapes_by_affaire_id', request_method='GET', renderer='json')
def affaires_etapes_view(request):
    """
    GET etapes affaire
    """
    # Check connected
    if not check_connected(request):
        raise exc.HTTPForbidden()

    affaire_id = request.matchdict['id']

    records = request.dbsession.query(VEtapesAffaires).filter(
        VEtapesAffaires.affaire_id == affaire_id
    ).order_by(
        VEtapesAffaires.next_datetime.desc()
    ).all()

    return Utils.serialize_many(records)


@view_config(route_name='etapes', request_method='POST', renderer='json')
@view_config(route_name='etapes_s', request_method='POST', renderer='json')
def etapes_new_view(request):
    """
    POST etapes affaire
    """
    # Check authorization
    if not check_connected(request):
        raise exc.HTTPForbidden()

    affaire_id = request.params['affaire_id'] if 'affaire_id' in request.params else None
    chef_equipe_id = request.params['chef_equipe_id'] if 'chef_equipe_id' in request.params else None
    operateur_id = request.params['operateur_id'] if 'operateur_id' in request.params else None
    
    # Add new step
    model = Utils.addNewRecord(request, AffaireEtape)

    # send mail
    affaire_etape_index = request.dbsession.query(AffaireEtapeIndex).filter(AffaireEtapeIndex.id == model.etape_id).first()
    etape_mailer = request.dbsession.query(EtapeMailer).filter(model.etape_id == EtapeMailer.etape_id).all()
    v_affaire = request.dbsession.query(VAffaire).filter(VAffaire.id == model.affaire_id).first()
    affaire = request.dbsession.query(Affaire).filter(Affaire.id == model.affaire_id).first()
    operateur = request.dbsession.query(Operateur).all()

    # get list of done steps
    lastSteps = request.dbsession.query(VEtapesAffaires).filter(
        and_(
            VEtapesAffaires.affaire_id == model.affaire_id,
            VEtapesAffaires.etape_priorite == int(request.registry.settings['affaire_etape_priorite_1_id'])
        )
    ).order_by(VEtapesAffaires.next_datetime.desc()).all()
    
    # set affaire_nom
    affaire_nom = " (" + affaire.no_access + ")" if affaire.no_access is not None else ""

    # only when chef_equipe is specified and chef equipe is not the initiator of new step
    mail_list = []
    if chef_equipe_id and (not chef_equipe_id == operateur_id):
        chef_equipe_mail = request.dbsession.query(Operateur).filter(Operateur.id == chef_equipe_id).first().mail
        if chef_equipe_mail is not None:
            mail_list.append( chef_equipe_mail )
        
        # update chef d'équipe in affaire
        affaire = request.dbsession.query(Affaire).filter(Affaire.id == model.affaire_id).first()
        affaire.technicien_id = chef_equipe_id

    # construct mail_list
    for em_i in etape_mailer:
        if em_i.sendmail:
            mail = next((op.mail for op in operateur if op.id == em_i.operateur_id), None)
            if mail:
                mail_list.append(mail)
    
    # Send mail only if step prio is 1 and if mail_list not empty
    if affaire_etape_index.priorite == int(request.registry.settings['affaire_etape_priorite_1_id']) and len(mail_list)>0:
        lastSteps_html = "".join(["<tr><td style='border: 1px solid black; border-collapse: collapse; padding: 5px 25px 5px 10px;'>{}</td>\
                              <td style='border: 1px solid black; border-collapse: collapse; padding: 5px 25px 5px 10px;'>{} {}</td>\
                              <td style='border: 1px solid black; border-collapse: collapse; padding: 5px 25px 5px 10px;'>{}</td>\
                              <td style='border: 1px solid black; border-collapse: collapse; padding: 5px 25px 5px 10px;'>{}</td>\
                              </tr>".format(
                                  i.etape, 
                                  i.next_operateur_prenom if i.next_operateur_prenom else "", 
                                  i.next_operateur_nom if i.next_operateur_nom else "", 
                                  i.next_datetime.strftime("%d.%m.%Y - %H:%M") if i.next_datetime else "", 
                                  i.next_remarque if i.next_remarque else ""
                                ) for i in lastSteps])
        
        text = "L'affaire <b><a href='" + os.path.join(request.registry.settings['infolica_url_base'], 'affaires/edit', str(v_affaire.id)) + "'>" + str(v_affaire.id) + affaire_nom + "</a></b>" + (" (avec mention urgente)" if v_affaire.urgent else "") + " est en attente pour l'étape <b>"+ affaire_etape_index.nom +"</b>."
        text += "<br><br>Cadastre: " + str(v_affaire.cadastre)
        text += "<br>Description: " + str(v_affaire.nom)
        text += ("<br><br><br><h4>Historique de l'affaire</h4>\
            <table style='border: 1px solid black; border-collapse: collapse; padding: 5px 25px 5px 10px;'>\
                <tr>\
                    <th style='border: 1px solid black; border-collapse: collapse; padding: 5px 25px 5px 10px;'>Étape</th>\
                    <th style='border: 1px solid black; border-collapse: collapse; padding: 5px 25px 5px 10px;'>Réalisée par</th>\
                    <th style='border: 1px solid black; border-collapse: collapse; padding: 5px 25px 5px 10px;'>Réalisée le</th>\
                    <th style='border: 1px solid black; border-collapse: collapse; padding: 5px 25px 5px 10px;'>Remarque</th>\
                </tr>" + lastSteps_html + "</table>") if lastSteps_html != "" else ""
        subject = "Infolica - affaire " + str(v_affaire.id) + (" - URGENT" if v_affaire.urgent else "")
        send_mail(request, mail_list, "", subject, html=text)

    # Finally erase attribution on affaire
    affaire.attribution = None

    # If last step was treatment & client_facture is outside of canton and has no SAP number, send mail to secretariat
    etape_traitement_id = int(request.registry.settings['affaire_etape_traitement_id'])

    if (len(lastSteps) > 1 and lastSteps[1].etape_id == etape_traitement_id):
        # get clients_facture
        clients_factures_id = request.dbsession.query(Facture.client_id).filter(Facture.affaire_id == affaire_id).all()
        clients_factures_id = [cl_id[0] for cl_id in clients_factures_id]
        clients_factures = request.dbsession.query(Client).filter(Client.id.in_(clients_factures_id)).all()

        # get npa from canton de Neuchâtel
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(parent_dir, "static", "npa_NE.txt"), "r") as f:
            lines = f.readlines()
            npa_NE = [int(line.rstrip()) for line in lines]

        for cl in clients_factures:
            if cl.no_sap is None and int(cl.npa) not in npa_NE:
                operateur_secretariat = request.registry.settings["operateur_secretariat"].split(",")
                mail_list = request.dbsession.query(Operateur.mail).filter(Operateur.id.in_(operateur_secretariat)).all()
                mail_list = [mail[0] for mail in mail_list]

                html = "<h3>Vérification de client</h3>"
                html += "<p>Un client hors canton et sans numéro SAP a été référencé dans la facturation de l'affaire <b><a href='" + os.path.join(request.registry.settings['infolica_url_base'], 'affaires/edit', str(affaire.id)) + "'>" + str(affaire.id) + affaire_nom + "</a></b>.</p>"
                html += "<ul><li>" + ", ".join([
                    cl.entreprise if cl.entreprise is not None else " ".join([
                        cl.titre if cl.titre is not None else "", 
                        cl.prenom if cl.prenom is not None else "", 
                        cl.nom if cl.nom is not None else ""
                    ]), 
                    cl.adresse if cl.adresse is not None else "", 
                    " ".join([
                            cl.npa if cl.npa is not None else "", 
                            cl.localite if cl.localite is not None else ""
                        ])
                    ]) + " &#8594; <a href='" + os.path.join(request.registry.settings['infolica_url_base'], 'clients/edit', str(cl.id)) + "'>Lien sur la fiche du client</a>"+ "</li></ul>"
                html += "<p>Merci d'entreprendre les démarches nécessaires pour corriger le client ou pour demander sa création dans SAP.</p>"
                send_mail(request, mail_list, "", "Infolica - Client hors canton à vérifier", html=html)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(AffaireEtape.__tablename__))


@view_config(route_name='etapes_by_id', request_method='DELETE', renderer='json')
def etapes_delete_view(request):
    """
    DELETE etapes affaire
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_etape_edition']):
        raise exc.HTTPForbidden()

    affaire_etape_id = request.matchdict['id']

    record = request.dbsession.query(AffaireEtape).filter(
        AffaireEtape.id == affaire_etape_id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(AffaireEtape.__tablename__, affaire_etape_id))

    request.dbsession.delete(record)

    return Utils.get_data_save_response(Constant.SUCCESS_DELETE.format(AffaireEtape.__tablename__))
