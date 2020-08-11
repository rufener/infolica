# -*- coding: utf-8 -*--
from datetime import date, datetime
from sqlalchemy import func, and_, desc
from infolica.models.models import Numero, AffaireNumero, Fonction, Role, FonctionRole
from infolica.scripts.ldap_query import LDAPQuery
import json
import os

unite_ppe_list = [
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
    'J',
    'K',
    'L',
    'M',
    'N',
    'O',
    'P',
    'Q',
    'R',
    'S',
    'T',
    'U',
    'V',
    'W',
    'X',
    'Y',
    'Z'
]


class Utils(object):

    @classmethod
    def serialize_one(cls, _query):
        """
        Serialize one query item
        """
        if _query is None:
            return None

        d = _query.__dict__
        item = {}
        for n in d.keys():
            if n != '_sa_instance_state':
                if isinstance(d[n], (datetime, date)):
                    item[n] = d[n].isoformat()
                else:
                    item[n] = d[n]

        return item

    @classmethod
    def serialize_many(cls, _query):
        """
        Serialize many query items
        """
        if _query is None:
            return None

        master = []
        for u in _query:
            d = u.__dict__
            item = {}
            for n in d.keys():
                if n != '_sa_instance_state':
                    if isinstance(d[n], (datetime, date)):
                        item[n] = d[n].isoformat()
                    else:
                        item[n] = d[n]
            master.append(item)
        return master

    @classmethod
    def get_model_record_attributes(cls, record):
        """
        Return model record parameters
        """
        return [a for a in dir(record) if not (a == 'id' or a.startswith('_'))] if record else []

    @classmethod
    def set_model_record(cls, record, params):
        """
        Set model record
        """
        atts = cls.get_model_record_attributes(record)

        for att in atts:
            if att != 'affaire_doc_file':
                val = params[att] if att in params else getattr(record, att)

                # Check boolean
                if val == 'true':
                    val = True
                if val == 'false':
                    val = False
                if val == "null":
                    val = None

                setattr(record, att, val)

        return record

    @classmethod
    def get_data_save_response(cls, message):
        """
        Get data save response
        """
        return {'message': message}

    @classmethod
    def get_search_conditions(cls, model, params):
        """
        Get search conditions
        """
        conditions = list()
        condition_not_in = False  # pour les conditions NOT IN, p. ex. référencement numéros à affaire

        for param in params:
            if param == 'matDiff':
                continue
            if param.startswith('_'):
                param = param[1:]
                condition_not_in = True
            
            if condition_not_in:
                conditions.append(~getattr(model, param).in_(json.loads(params["_"+param])))
                condition_not_in = False
            else:
                if params[param].isdigit() and not param == 'npa':
                    tmp = int(params[param])
                    conditions.append(getattr(model, param) == tmp)
                else:
                    conditions.append(func.lower(getattr(model, param)).like(
                        '%' + func.lower(params[param].replace('"', '')) + '%'))
        return conditions

    @classmethod
    def last_number(cls, request, cadastre_id, type_id, plan_id=None, affaire_id=None):
        """
        Get number_record with the highest number in cadastre and type
        to continue the numerotation
        """
        if not isinstance(type_id, list):
            type_id = [type_id]
        # Filter by type and cadastre
        query = request.dbsession.query(Numero).filter(
            and_(Numero.type_id.in_(type_id), Numero.cadastre_id == cadastre_id)
        )
        # If plan_id is specified, also filter by plan
        if plan_id:
            query = query.filter(Numero.plan_id == plan_id)
        if affaire_id:
            query = query.filter(
                and_(AffaireNumero.affaire_id == affaire_id, AffaireNumero.numero_id == Numero.id)
            )
        result = query.order_by(desc(Numero.numero)).limit(1).first()
        numero = result.numero if result else 0
        return numero

    @classmethod
    def _params(cls, **kwargs):
        """
        Function that creates dictionnary with specified keys and values
        """
        params = dict()
        for key, value in kwargs.items():
            params[key] = value
        return params

    @classmethod
    def get_unite_from_index(cls, idx):
        """
        Get PPE unite from index
        """
        if idx == 0:
            unite = "A"
        else:
            n = len(unite_ppe_list)
            unite = ""
            c = 0
            while idx: 
                idx, idx_ = divmod(idx-c, n)
                unite = unite_ppe_list[idx_] + unite
                c = 1
        return unite

    @classmethod
    def get_index_from_unite(cls, unite):
        """
        Get index from PPE unite
        """
        n = len(unite_ppe_list)
        idx = 0
        c = 0
        for i, unite_i in enumerate(reversed(list(unite))):
            idx = idx + (unite_ppe_list.index(unite_i) + c) * n**i
            c = 1
        return idx

    @classmethod
    def get_fonctions_roles_by_id(cls, request, role_id):
        """
        Return fonctions roles by role id
        """
        results = []

        query = request.dbsession.query(Fonction, Role, FonctionRole).filter(
            Role.id == role_id).filter(Role.id == FonctionRole.role_id).filter(
            Fonction.id == FonctionRole.fonction_id).all()

        for f, r, fr in query:
            one_item = {}
            one_item["id"] = f.id
            one_item["nom"] = f.nom

            results.append(one_item)

        return results

    @classmethod
    def get_fonctions_roles_by_name(cls, request, role_name):
        results = []

        query = request.dbsession.query(Fonction, Role, FonctionRole).filter(
            Role.nom == role_name).filter(Role.id == FonctionRole.role_id).filter(
            Fonction.id == FonctionRole.fonction_id).all()

        for f, r, fr in query:
            one_item = {}
            one_item["id"] = f.id
            one_item["nom"] = f.nom

            results.append(one_item)

        return results

    @classmethod
    def has_permission(cls, request, fonction_name):
        if not cls.check_connected(request):
            return False

        user_dn = request.authenticated_userid

        if not user_dn:
            return False

        role_name = LDAPQuery.get_user_group_by_dn(request, user_dn)

        fonctions = cls.get_fonctions_roles_by_name(request, role_name)
        fonctions_names = [x for x in fonctions if x["nom"] == fonction_name]
        return len(fonctions_names) > 0

    @classmethod
    def check_connected(cls, request):
        auth_tkt = request.cookies.get('auth_tkt', default=None)

        if not auth_tkt:
            return False

        return True

    @classmethod
    def get_role_id_by_name(cls, request, role_name):
        query = request.dbsession.query(Role).filter(
            Role.nom == role_name).first()

        if query:
            return query.id

        return None

    @classmethod
    def get_nouveaux_operateurs_ad(cls, request):
        return LDAPQuery.get_infolica_users(request)

    @classmethod
    def create_affaire_folder(cls, affaire_folder):
        if not os.path.isdir(affaire_folder):
            os.mkdir(affaire_folder)

