# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from sqlalchemy import and_

from infolica.exceptions.custom_error import CustomError
from infolica.models.constant import Constant
from infolica.models.models import AffaireNumero, Numero, NumeroDiffere, NumeroEtat
from infolica.models.models import NumeroEtatHisto, NumeroType, VNumeros
from infolica.models.models import VNumerosAffaires
from infolica.scripts.utils import Utils

import json


@view_config(route_name='numeros', request_method='GET', renderer='json')
@view_config(route_name='numeros_s', request_method='GET', renderer='json')
def numeros_view(request):
    """
    Return all numeros
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    numero = int(request.params['numero']) if 'numero' in request.params else None
    cadastre_id = [int(a) for a in request.params['cadastre_id'].split(",")] if 'cadastre_id' in request.params else None
    type_id = [int(a) for a in request.params['type_id'].split(",")] if 'type_id' in request.params else None
    etat_id = [int(a) for a in request.params['etat_id'].split(",")] if 'etat_id' in request.params else None

    query = request.dbsession.query(VNumeros)
    
    if numero:
        query = query.filter(VNumeros.numero == numero)
    if cadastre_id:
        query = query.filter(VNumeros.cadastre_id.in_(cadastre_id))
    if type_id:
        query = query.filter(VNumeros.type_numero_id.in_(type_id))
    if etat_id:
        query = query.filter(VNumeros.etat_id.in_(etat_id))

    query = query.order_by(VNumeros.numero.asc()).all()

    return Utils.serialize_many(query)


@view_config(route_name='types_numeros', request_method='GET', renderer='json')
@view_config(route_name='types_numeros_s', request_method='GET', renderer='json')
def types_numeros_view(request):
    """
    Return all types_numeros
    """
    query = request.dbsession.query(NumeroType).filter(NumeroType.ordre != None).order_by(NumeroType.ordre.asc()).all()
    return Utils.serialize_many(query)


@view_config(route_name='etats_numeros', request_method='GET', renderer='json')
@view_config(route_name='etats_numeros_s', request_method='GET', renderer='json')
def etats_numeros_view(request):
    """
    Return all etats_numeros
    """
    id_artefact = request.registry.settings['numero_artefact_id']
    query = request.dbsession.query(NumeroEtat).filter(NumeroEtat.id != id_artefact).all()
    return Utils.serialize_many(query)


@view_config(route_name='numero_by_id', request_method='GET', renderer='json')
def numeros_by_id_view(request):
    """
    Return numeros by id
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    id = request.id = request.matchdict['id']
    query = request.dbsession.query(VNumeros).filter(
        VNumeros.id == id).first()
    return Utils.serialize_one(query)


@view_config(route_name='recherche_numeros', request_method='POST', renderer='json')
@view_config(route_name='recherche_numeros_s', request_method='POST', renderer='json')
def numeros_search_view(request):
    """
    Search numeros
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    settings = request.registry.settings
    search_limit = int(settings['search_limit'])

    params = request.params

    matDiff = False
    if 'matDiff' in params:
        matDiff = True if params['matDiff'] == 'true' else False

    # Set conditions
    conditions = Utils.get_search_conditions(VNumeros, params)

    # filter by conditions
    query = request.dbsession.query(VNumeros).order_by(
        VNumeros.cadastre,
        VNumeros.numero.desc()
    ).filter(*conditions)

    # if option matDiff selected
    if matDiff:
        query = query.filter(
            and_(
                VNumeros.diff_entree.isnot(None),
                VNumeros.diff_sortie.is_(None)
                )
            )

    query = query.limit(search_limit).all()
    return Utils.serialize_many(query)


@view_config(route_name='numeros', request_method='POST', renderer='json')
@view_config(route_name='numeros_s', request_method='POST', renderer='json')
def numeros_new_view(request, params=None):
    """
    Add new numeros
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()

    if not params:
        params = request.params

    # nouveau numero
    record = Numero()
    record = Utils.set_model_record(record, params)

    request.dbsession.add(record)
    request.dbsession.flush()

    Utils.get_data_save_response(
            Constant.SUCCESS_SAVE.format(Numero.__tablename__)
    )

    return record.id


@view_config(route_name='numeros', request_method='PUT', renderer='json')
@view_config(route_name='numeros_s', request_method='PUT', renderer='json')
def numeros_update_view(request):
    """
    Update numeros
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()

    # Get numero id
    id = request.params['id'] if 'id' in request.params else None

    # Get numero record
    record = request.dbsession.query(Numero).filter(
        Numero.id == id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(Numero.__tablename__, id))

    last_record_etat_id = record.etat_id
    record = Utils.set_model_record(record, request.params)

    if 'etat_id' in request.params:
        if request.params['etat_id'] != last_record_etat_id:
            params = Utils._params(
                numero_id=record.id, numero_etat_id=request.params['etat_id'])
            numeros_etat_histo_new_view(request, params)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Numero.__tablename__))


@view_config(route_name='numero_by_id', request_method='DELETE', renderer='json')
def numeros_by_id_delete_view(request):
    """
    Supprimer/abandonner numeros by id
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()

    settings = request.registry.settings
    projet_id = int(settings['numero_projet_id'])
    abandonne_id = int(settings['numero_abandonne_id'])

    # Get numero by id
    id = request.matchdict['id']
    query = request.dbsession.query(Numero).filter(
        Numero.id == id).first()

    if query:
        if query.etat_id == projet_id:
            query.etat_id = abandonne_id
        elif query.etat_id == abandonne_id:
            query.etat_id = projet_id


###########################################################
# NUMERO ETAT HISTO
###########################################################


@view_config(route_name='numeros_etat_histo', request_method='POST', renderer='json')
@view_config(route_name='numeros_etat_histo_s', request_method='POST', renderer='json')
def numeros_etat_histo_new_view(request, params=None):
    """
    Add new numero_etat_histo
    """
    # Check authorization
    settings = request.registry.settings
    if not Utils.has_permission(request, settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()

    if not params:
        params = request.params

    # nouveau numero
    record = NumeroEtatHisto()
    record = Utils.set_model_record(record, params)

    request.dbsession.add(record)
    request.dbsession.flush()

    Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(
        NumeroEtatHisto.__tablename__)
    )

    return record.id

###########################################################
# AFFAIRE-NUMERO
###########################################################


@view_config(route_name='affaire_numeros_by_affaire_id', request_method='GET', renderer='json')
def affaire_numeros_view(request):
    """
    Add new numero_etat_histo
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()
    conditions = list()
    affaire_id = request.matchdict["id"]

    # Récupérer les id des numéros de la MO
    settings = request.registry.settings

    numeros_immeubles_type_id = [
        settings['numero_bf_id'],
        settings['numero_ddp_id'],
        settings['numero_ppe_id'],
        settings['numero_pcop_id']
    ]

    conditions.append(VNumerosAffaires.affaire_id == affaire_id)
    conditions.append(VNumerosAffaires.numero_type_id.in_(numeros_immeubles_type_id))

    if 'affaire_numero_actif' in request.params:
        affaire_numero_actif = request.params['affaire_numero_actif']
        affaire_numero_actif = True if affaire_numero_actif.upper() == 'TRUE' else False
        conditions.append(VNumerosAffaires.affaire_numero_actif == affaire_numero_actif)

    records = request.dbsession.query(VNumerosAffaires).filter(
        *conditions).all()
    return Utils.serialize_many(records)


@view_config(route_name='affaire_new_numeros_MO_by_affaire_id', request_method='GET', renderer='json')
def affaire_new_numeros_mo_view(request):
    """
    Return all new numeros MO in affaire
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    affaire_id = request.matchdict["id"]

    # Récupérer les id des numéros de la MO
    settings = request.registry.settings

    numeros_mo_type_id = [
        settings['numero_pfp3_id'],
        settings['numero_bat_id'],
        settings['numero_pcs_id'],
        settings['numero_paux_id'],
        settings['numero_pdet_id'],
        settings['numero_dp_id']
    ]

    # Contenu de la table VNumerosAffaires avec les numéros de la MO
    query = request.dbsession.query(VNumerosAffaires).filter(
        and_(
            VNumerosAffaires.affaire_id == affaire_id,
            VNumerosAffaires.numero_type_id.in_(numeros_mo_type_id)
        )
    )

    records = query.all()

    cadastres_id = list()
    types_id = list()
    plans_id = list()
    for record in records:
        cadastres_id.append(record.numero_cadastre_id)
        types_id.append(record.numero_type_id)
        plans_id.append(record.numero_plan_id)
    # Retient les valeurs uniques
    cadastres_id = set(cadastres_id)
    types_id = set(types_id)
    plans_id = set(plans_id)

    reservations_ranges = list()
    for cadastre_id in cadastres_id:
        for type_id in types_id:
            for plan_id in plans_id:
                records = query.filter(
                    and_(
                        VNumerosAffaires.numero_cadastre_id == cadastre_id,
                        VNumerosAffaires.numero_type_id == type_id,
                        VNumerosAffaires.numero_plan_id == plan_id
                    )
                ).order_by(VNumerosAffaires.numero.asc()).all()

                if len(records) == 0:
                    continue

                numeros = list()
                for record in records:
                    numeros.append(record.numero)

                # Get lists of consecutive numbers [[de, à], [de, à], etc]
                consecutive_diff = [x - numeros[i - 1] for i, x in enumerate(numeros)][1:]
                diff_index_greaterthan1 = list(filter(lambda x: consecutive_diff[x] > 1, range(len(consecutive_diff))))

                last_diff_idx = 0
                for i, diff_idx in enumerate(diff_index_greaterthan1):

                    reservations_ranges.append({
                        "cadastre_id": cadastre_id,
                        "type_id": type_id,
                        "plan_id": plan_id,
                        "numero_de": numeros[last_diff_idx],
                        "numero_a": numeros[diff_idx],
                        "cadastre": record.numero_cadastre,
                        "numero_type": record.numero_type,
                        "nombre": numeros[diff_idx] - numeros[last_diff_idx] + 1
                    })

                    last_diff_idx = diff_idx + 1

                # Ne pas oublier la dernière série...
                reservations_ranges.append({
                    "cadastre_id": cadastre_id,
                    "type_id": type_id,
                    "plan_id": plan_id,
                    "numero_de": numeros[last_diff_idx],
                    "numero_a": numeros[-1],
                    "cadastre": record.numero_cadastre,
                    "numero_type": record.numero_type,
                    "nombre": numeros[-1] - numeros[last_diff_idx] + 1
                })

    return json.loads(json.dumps(reservations_ranges))


@view_config(route_name='affaire_numeros', request_method='PUT', renderer='json')
@view_config(route_name='affaire_numeros_s', request_method='PUT', renderer='json')
def affaire_numero_update_view(request):
    """
    Update numeros_affaires
    """
    if not Utils.has_permission(request, request.registry.settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()

    affnum_id = request.params["id"] if "id" in request.params else None

    record = request.dbsession.query(AffaireNumero).filter(AffaireNumero.id == affnum_id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(AffaireNumero.__tablename__, affnum_id))

    record = Utils.set_model_record(record, request.params)

    return


@view_config(route_name='affaire_numeros', request_method='POST', renderer='json')
@view_config(route_name='affaire_numeros_s', request_method='POST', renderer='json')
def affaire_numero_new_view(request, params=None):
    """
    Add new affaire-numero
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()

    if not params:
        params = request.params
    # nouveau affaire_numero
    record = AffaireNumero()
    record = Utils.set_model_record(record, params)

    request.dbsession.add(record)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(AffaireNumero.__tablename__))


###########################################################
# NUMERO- AFFAIRE
###########################################################

@view_config(route_name='numero_affaires_by_numero_id', request_method='GET', renderer='json')
def numeros_affaire_view(request):
    """
    Get new affaire-numero
    """
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    numero_id = request.matchdict['id']

    query = request.dbsession.query(VNumerosAffaires).filter(
        VNumerosAffaires.numero_id == numero_id).all()

    if not query:
        raise CustomError.RECORD_WITH_ID_NOT_FOUND.format(
            VNumerosAffaires.__tablename__, numero_id)

    return Utils.serialize_many(query)


###########################################################
# NUMERO DIFFERE
###########################################################

@view_config(route_name='numeros_differes', request_method='POST', renderer='json')
@view_config(route_name='numeros_differes_s', request_method='POST', renderer='json')
def numero_differe_new_view(request):
    """
    Add new numero_differe
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()

    # nouveau numero_differe
    record = NumeroDiffere()
    record = Utils.set_model_record(record, request.params)

    request.dbsession.add(record)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(NumeroDiffere.__tablename__))


@view_config(route_name='numeros_differes', request_method='PUT', renderer='json')
@view_config(route_name='numeros_differes_s', request_method='PUT', renderer='json')
def numero_differe_update_view(request):
    """
    Update numero_differe
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()

    numdiff_id = request.params["numero_diff_id"] if "numero_diff_id" in request.params else None

    # update numero_differe
    record = request.dbsession.query(NumeroDiffere).filter(NumeroDiffere.id == numdiff_id).first()
    record = Utils.set_model_record(record, request.params)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(NumeroDiffere.__tablename__))
