# -*- coding: utf-8 -*--
from datetime import date, datetime
from sqlalchemy import func, and_, desc
from sqlalchemy import String
from sqlalchemy.sql.expression import cast
from infolica.models.models import Preavis, PreavisRemarque, Plan
from infolica.models.models import Numero, AffaireNumero, AffaireEtape
from infolica.models.models import Role, ReservationNumerosMO, Operateur
from infolica.scripts.authentication import get_user_functions, check_connected

from shutil import copytree, ignore_patterns
from docxtpl import DocxTemplate, RichText
import json
import os
import time

unite_ppe_list = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]


class Utils(object):
    @classmethod
    def date_isoformat(cls, date_):
        if isinstance(date_, (datetime, date)):
            return date_.isoformat()
        return date_

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
            if n != "_sa_instance_state" and n != "geom":
                item[n] = cls.date_isoformat(d[n])

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
                if n != "_sa_instance_state" and n != "geom":
                    item[n] = cls.date_isoformat(d[n])
            master.append(item)
        return master

    @classmethod
    def get_model_record_attributes(cls, record):
        """
        Return model record parameters
        """
        return [a for a in dir(record) if not (a == "id" or a.startswith("_"))] if record else []

    @classmethod
    def set_model_record(cls, record, params):
        """
        Set model record
        """
        atts = cls.get_model_record_attributes(record)

        for att in atts:
            if att != "affaire_doc_file":
                val = params[att] if att in params else getattr(record, att)

                # Check boolean
                if val == "true":
                    val = True
                if val == "false":
                    val = False
                if val == "null" or val == "":
                    val = None

                setattr(record, att, val)

        return record

    @classmethod
    def get_data_save_response(cls, message):
        """
        Get data save response
        """
        return {"message": message}

    @classmethod
    def get_search_conditions(cls, model, params, ignore_params=[]):
        """
        Get search conditions
        """
        conditions = list()

        for param in params:
            if param in ignore_params:
                continue
            if param.startswith("_"):
                # pour les conditions NOT IN, p. ex. référencement numéros à affaire
                param = param[1:]
                conditions.append(~getattr(model, param).in_(json.loads(params["_" + param])))
            elif param.startswith("%"):
                # pour les conditions numérique qui contiennent un sous ensemble (p.ex. 101 est contenu dans 2101)
                param = param[1:]
                conditions.append(cast(getattr(model, param), String).like("%" + params["%" + param] + "%"))
            else:
                if params[param].isdigit() and not param == "npa" and not param == "no_access":
                    tmp = int(params[param])
                    conditions.append(getattr(model, param) == tmp)
                else:
                    conditions.append(func.lower(getattr(model, param)).like("%" + func.lower(params[param].replace('"', "")) + "%"))
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
        query = request.dbsession.query(Numero).filter(and_(Numero.type_id.in_(type_id), Numero.cadastre_id == cadastre_id))
        # If plan_id is specified, also filter by plan
        if plan_id:
            query = query.filter(Numero.plan_id == plan_id)
        if affaire_id:
            query = query.filter(and_(AffaireNumero.affaire_id == affaire_id, AffaireNumero.numero_id == Numero.id))
        result = query.order_by(desc(Numero.numero)).limit(1).first()
        numero = result.numero if result else 0
        return numero

    @classmethod
    def last_number_mo(cls, request, cadastre_id, type_id, plan_id=None):
        """
        Return last number MO taking into account twin cadastres
        """
        query = request.dbsession.query(func.max(ReservationNumerosMO.numero_a)).filter(and_(ReservationNumerosMO.cadastre_id == cadastre_id, ReservationNumerosMO.type_id == type_id))

        if plan_id:
            plan = request.dbsession.query(Plan).filter(Plan.idobj == plan_id).first()
            _, plan_no = plan.id_obj2.split("_")

            query = query.filter(ReservationNumerosMO.plan == plan_no)

        return 0 if query.first()[0] is None else query.first()[0]

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
                idx, idx_ = divmod(idx - c, n)
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

        role = request.dbsession.query(Role).get(role_id)

        functions = role.fonctions

        for function in functions:
            results.append({"id": function.id, "nom": function.nom})

        return results

    @classmethod
    def has_permission(cls, request, fonction_name):
        if not check_connected(request):
            return False

        user_functions = get_user_functions(request)

        if fonction_name in user_functions["fonctions"]:
            return True

        return False

    @classmethod
    def get_role_id_by_name(cls, request, role_name):
        query = request.dbsession.query(Role).filter(Role.nom == role_name).first()

        if query:
            return query.id

        return None

    @classmethod
    def create_affaire_folder(cls, template_path, affaire_path):
        if not os.path.isdir(affaire_path):
            copytree(template_path, affaire_path, ignore=ignore_patterns("Thumbs.db"))
            settime = time.time()
            os.utime(affaire_path, times=(settime, settime))
        return

    @classmethod
    def addNewRecord(cls, request, Model, params=None):
        """
        Create a new record in table Model. This is a general case, with no supplementary condition.
        Returns id of the new record.
        Uses params if set, request.params otherwise.
        """
        if params is None:
            params = request.params

        record = Model()
        record = cls.set_model_record(record, params)
        request.dbsession.add(record)
        request.dbsession.flush()
        return record

    @classmethod
    def getOperateurFromUser(cls, request):
        user = request.authenticated_userid
        operateur = request.dbsession.query(Operateur).filter(func.lower(Operateur.login) == user).first()
        return operateur

    @classmethod
    def check_unread_preavis_remarks(cls, request, affaire_id, service_id=None):

        preavis_remarques = (
            request.dbsession.query(PreavisRemarque.operateur_id)
            .join(Preavis, Preavis.id == PreavisRemarque.preavis_id, isouter=True)
            .filter(
                Preavis.affaire_id == affaire_id,
                PreavisRemarque.lu_operateur_id == None,
            )
        )

        if service_id is not None:
            preavis_remarques = preavis_remarques.filter(Preavis.service_id == service_id)

        preavis_remarques = preavis_remarques.all()

        connectedUser = cls.getOperateurFromUser(request)
        pr_remark_user_query = request.dbsession.query(Operateur)

        unread = 0
        if len(preavis_remarques) > 0:
            for pr in preavis_remarques:
                pr_remark_user = pr_remark_user_query.filter(Operateur.id == pr[0]).first()
                if not connectedUser.service_id == pr_remark_user.service_id:
                    unread += 1

        return unread

    @classmethod
    def generate_file_from_template(cls, request, template, data, output_file_name, timeout=5):
        settings = request.registry.settings
        mails_templates_directory = settings["mails_templates_directory"]
        temporary_directory = settings["temporary_directory"]

        # Set output file name
        date_time = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = output_file_name + "_" + date_time + ".docx"
        file_path = os.path.join(temporary_directory, filename)

        # Set context
        for key in data.keys():
            if type(data[key]) is tuple:
                if data[key][0] is True or data[key][0] is False:
                    continue
                data[key] = RichText(data[key][0], **data[key][1])
            else:
                if data[key] is True or data[key] is False:
                    continue
                data[key] = RichText(data[key])

        # Ouverture du document template
        doc = DocxTemplate(os.path.join(mails_templates_directory, template + ".docx"))

        # Replace values by keywords and save
        doc.render(data)
        doc.save(file_path)

        return filename

    @classmethod
    def newAffaireEtape(cls, request, affaire_id, etape_id, remarque=None, operateur_id=None, datetime_=datetime.now()):

        if operateur_id is None:
            operateur_id = (cls.getOperateurFromUser(request).id,)

        params = Utils._params(affaire_id=affaire_id, etape_id=etape_id, operateur_id=operateur_id, datetime=datetime_, remarque=remarque)

        record = AffaireEtape()
        record = Utils.set_model_record(record, params)
        request.dbsession.add(record)

        return

    @classmethod
    def affaireUpdatePermission(cls, request, affaire_type):
        permission = request.registry.settings["affaire_edition"]

        # Affaire de cadastration
        if affaire_type == request.registry.settings["affaire_type_cadastration_id"]:
            permission = request.registry.settings["affaire_cadastration_edition"]
        # Affaire de PPE
        elif affaire_type == request.registry.settings["affaire_type_ppe_id"]:
            permission = request.registry.settings["affaire_ppe_edition"]
        # Affaire de révision d'abornement
        elif affaire_type == request.registry.settings["affaire_type_revision_abornement_id"]:
            permission = request.registry.settings["affaire_revision_abornement_edition"]
        # Affaire de rétablissement de PFP3
        elif affaire_type == request.registry.settings["affaire_type_retablissement_pfp3_id"]:
            permission = request.registry.settings["affaire_retablissement_pfp3_edition"]
        # Affaire pcop
        elif affaire_type == request.registry.settings["affaire_type_part_copropriete_id"]:
            permission = request.registry.settings["affaire_pcop_edition"]
        # Affaire mpd
        elif affaire_type == request.registry.settings["affaire_type_mpd_id"]:
            permission = request.registry.settings["affaire_mpd_edition"]
        # Affaire autre
        elif affaire_type == request.registry.settings["affaire_type_autre_id"]:
            permission = request.registry.settings["affaire_autre_edition"]
        # Affaire affaire_type_remaniement_parcellaire_id
        elif affaire_type == request.registry.settings["affaire_type_remaniement_parcellaire_id"]:
            permission = request.registry.settings["affaire_remaniement_parcellaire_edition"]

        return permission

    @classmethod
    def clientAdressFormatter(cls, client, premiere_ligne="", sep=", ", shortened=False):
        adress = ""

        tmp = []
        if shortened:
            if client.type_client in [2, 3]:
                tmp.append(premiere_ligne)
                tmp.append("Par " + client.entreprise if premiere_ligne else client.entreprise)
                adress = sep.join(filter(None, tmp))

            elif client.type_client in [1]:
                tmp.append(premiere_ligne)
                tmp.append(" ".join(filter(None, [("Par " if premiere_ligne else None), client.titre, client.prenom, client.nom]))),
                adress = sep.join(filter(None, tmp))

        else:
            if client.type_client in [2, 3]:
                tmp.append(premiere_ligne)
                tmp.append("Par " + client.entreprise if premiere_ligne else client.entreprise)
                tmp.append(client.co)
                tmp.append(client.adresse)
                tmp.append(" ".join(filter(None, [client.npa, client.localite])))
                adress = sep.join(filter(None, tmp))

            elif client.type_client in [1]:
                tmp.append(premiere_ligne)
                tmp.append(" ".join(filter(None, [("Par " if premiere_ligne else None), client.titre, client.prenom, client.nom]))),
                tmp.append(client.co)
                tmp.append(client.adresse)
                tmp.append(" ".join(filter(None, [client.npa, client.localite])))
                adress = sep.join(filter(None, tmp))

        return adress

    @classmethod
    def clientRemarkBuilder(cls, client, sep="\n", checkNeedFactureReference=True, checkNeedOtherClientFacture=True):
        remarque = []
        if checkNeedFactureReference is True and client.besoin_vref_facture is True:
            remarque.append("Le client demande une référence dans la facture.")
        if checkNeedOtherClientFacture is True and client.besoin_client_facture is True:
            remarque.append("Le client demande une adresse de facturation différente.")
        remarque = sep.join(remarque)
        return remarque
