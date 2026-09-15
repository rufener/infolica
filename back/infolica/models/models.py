from sqlalchemy import Column, Integer, BigInteger, Float, Text, String, Date, DateTime, Interval, Boolean, ARRAY, ForeignKey, UniqueConstraint, Table, text, Uuid

from sqlalchemy.orm import relationship

from geoalchemy2 import Geometry

import datetime
from .constant import Constant
from .meta import Base

association_fonction_role = Table("fonction_role", Base.metadata, Column("id", primary_key=True), Column("role_id", ForeignKey("role.id"), nullable=False), Column("fonction_id", ForeignKey("fonction.id"), nullable=False))


class Role(Base):
    __tablename__ = "role"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)
    fonctions = relationship("Fonction", secondary=association_fonction_role)


class Fonction(Base):
    __tablename__ = "fonction"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class Service(Base):
    __tablename__ = "service"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    service = Column(Text, nullable=False)
    abreviation = Column(Text, nullable=False)
    titre = Column(Text)
    nom = Column(Text)
    prenom = Column(Text)
    adresse = Column(Text)
    case_postale = Column(Text)
    npa = Column(Text)
    localite = Column(Text)
    telephone = Column(Text)
    mail = Column(Text)
    ordre = Column(BigInteger)
    relpath = Column(Text)
    date_entree = Column(Date)
    date_sortie = Column(Date)
    service_principal = Column(Boolean)


class Operateur(Base):
    __tablename__ = "operateur"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)
    prenom = Column(Text, nullable=False)
    initiales = Column(Text)
    login = Column(Text)  # , nullable=False)
    responsable = Column(Boolean, default=False, nullable=False)
    chef_equipe = Column(Boolean, default=False, nullable=False)
    entree = Column(Date, default=datetime.datetime.utcnow, nullable=False)
    sortie = Column(Date)
    mail = Column(Text)
    last_notemaj_id = Column(BigInteger)
    role_id = Column(BigInteger, ForeignKey(Role.id))
    service = Column(Text)
    service_id = Column(BigInteger, ForeignKey(Service.id))
    ldap_domain = Column(String(5))
    role = relationship("Role", uselist=False)


class Cadastre(Base):
    __tablename__ = "cadastre"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)
    service_urbanisme_id = Column(BigInteger, ForeignKey(Service.id))


class ClientType(Base):
    __tablename__ = "client_type"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class Client(Base):
    __tablename__ = "client"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type_client = Column(BigInteger, ForeignKey(ClientType.id), nullable=False)
    entreprise = Column(Text)
    titre = Column(Text)
    nom = Column(Text)
    prenom = Column(Text)
    represente_par = Column(Text)
    co = Column(Text)
    adresse = Column(Text)
    npa = Column(Text)
    localite = Column(Text)
    case_postale = Column(Text)
    tel_fixe = Column(Text)
    fax = Column(Text)
    tel_portable = Column(Text)
    mail = Column(Text)
    entree = Column(Date, default=datetime.datetime.utcnow, nullable=False)
    sortie = Column(Date)
    no_sap = Column(Text)
    no_bdp_bdee = Column(Text)
    no_access = Column(Text)
    besoin_vref_facture = Column(Boolean)
    besoin_client_facture = Column(Boolean)


class ClientMoralPersonne(Base):
    __tablename__ = "client_moral_personne"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    client_id = Column(BigInteger, ForeignKey(Client.id), nullable=False)
    titre = Column(Text)
    nom = Column(Text, nullable=False)
    prenom = Column(Text, nullable=False)


class Plan(Base):
    __tablename__ = "mo_distr_plan"
    __table_args__ = {"schema": "infolica"}
    idobj = Column(Text, primary_key=True)
    id_obj2 = Column(Text)
    planno = Column(Text)
    typlan = Column(Text)
    datmev = Column(Text)
    statut = Column(Text)
    echell = Column(Integer)
    idborplan = Column(Text)
    idrepplan = Column(Text)
    base = Column(Text)
    geom = Column(Geometry("MULTIPOLYGON"))


class AffaireType(Base):
    __tablename__ = "affaire_type"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)
    ordre = Column(BigInteger)
    reservation_numeros_types_id = Column(ARRAY(BigInteger))
    modif_affaire_type_id_vers = Column(ARRAY(BigInteger))
    logique_processus = Column(ARRAY(BigInteger))
    affaire_section_suivi = Column(Boolean, server_default=text("true"))
    affaire_section_preavis = Column(Boolean, server_default=text("false"))
    affaire_section_numeros = Column(Boolean, server_default=text("true"))
    affaire_section_facture = Column(Boolean, server_default=text("false"))
    affaire_section_ctrl_chefprojet_mo = Column(Boolean, server_default=text("false"))
    affaire_section_ctrl_chefprojet_ppe = Column(Boolean, server_default=text("false"))
    affaire_section_ctrl_coordprojets = Column(Boolean, server_default=text("false"))
    affaire_section_ctrl_geometre = Column(Boolean, server_default=text("false"))
    affaire_section_documents = Column(Boolean, server_default=text("true"))


class Affaire(Base):
    __tablename__ = "affaire"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    no_access = Column(Text)
    nom = Column(Text)
    client_commande_id = Column(BigInteger, ForeignKey(Client.id))
    client_commande_complement = Column(Text)
    client_envoi_id = Column(BigInteger, ForeignKey(Client.id))
    client_envoi_complement = Column(Text)
    technicien_id = Column(BigInteger, ForeignKey(Operateur.id))
    type_id = Column(BigInteger, ForeignKey(AffaireType.id), nullable=False)
    cadastre_id = Column(BigInteger, ForeignKey(Cadastre.id), nullable=False)
    information = Column(Text)
    date_ouverture = Column(Date, default=datetime.datetime.utcnow, nullable=False)
    date_validation = Column(Date)
    date_envoi = Column(Date)
    date_cloture = Column(Date)
    localisation_E = Column(Float, nullable=False)
    localisation_N = Column(Float, nullable=False)
    vref = Column(Text)
    chemin = Column(Text)
    abandon = Column(Boolean, nullable=False, default=False)
    resume = Column(Text)
    urgent = Column(Boolean)
    urgent_echeance = Column(Date)
    attribution = Column(Text)
    uuid = Column(Uuid)
    last_changed_uuid = Column(Date)


class AffaireEtapeIndex(Base):
    __tablename__ = "affaire_etape_index"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)
    ordre = Column(BigInteger)
    priorite = Column(Integer)


class AffaireEtape(Base):
    __tablename__ = "affaire_etape"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    operateur_id = Column(BigInteger, ForeignKey(Operateur.id))
    etape_id = Column(BigInteger, ForeignKey(AffaireEtapeIndex.id), nullable=False)
    datetime = Column(DateTime, nullable=False)
    nb_jours_hors_sgrf = Column(Integer, default=0)
    hors_sgrf_de = Column(Date)
    hors_sgrf_a = Column(Date)
    remarque = Column(Text)


class ModificationAffaireType(Base):
    __tablename__ = "modification_affaire_type"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)
    ordre = Column(BigInteger)
    reservation_numeros_types_id = Column(ARRAY(BigInteger))
    affaire_source_type_id = Column(ARRAY(BigInteger))
    affaire_destination_type_id = Column(BigInteger, ForeignKey(AffaireType.id))


class ModificationAffaire(Base):
    __tablename__ = "modification_affaire"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id_mere = Column(Integer, ForeignKey(Affaire.id), nullable=False)
    affaire_id_fille = Column(Integer, ForeignKey(Affaire.id), nullable=False)
    type_id = Column(BigInteger, ForeignKey(ModificationAffaireType.id), nullable=False)
    date = Column(Date, default=datetime.datetime.utcnow, nullable=False)


class FactureType(Base):
    __tablename__ = "facture_type"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class FactureParametres(Base):
    __tablename__ = "facture_parametres"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)
    valeur = Column(Float, nullable=False)
    valable_de = Column(Date, nullable=False)
    valable_a = Column(Date, nullable=True)


class Facture(Base):
    __tablename__ = "facture"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type_id = Column(BigInteger, ForeignKey(FactureType.id), nullable=False)
    sap = Column(Text)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    client_id = Column(BigInteger, ForeignKey(Client.id), nullable=False)
    client_co_id = Column(BigInteger, ForeignKey(Client.id))
    client_complement = Column(Text)
    client_premiere_ligne = Column(Text)
    montant_mo = Column(Float, default=0.0, nullable=False)
    montant_rf = Column(Float, default=0.0, nullable=False)
    montant_mat_diff = Column(Float, default=0.0, nullable=False)
    montant_tva = Column(Float, default=0.0, nullable=False)
    montant_total = Column(Float, default=0.0, nullable=False)
    date = Column(Date)
    remarque = Column(Text)
    numeros = Column(ARRAY(BigInteger))


class TableauEmoluments(Base):
    __tablename__ = "tableau_emoluments"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    domaine = Column(Text, nullable=False)
    categorie = Column(Text, nullable=False)
    categorie_id = Column(Integer)
    sous_categorie = Column(Text, nullable=False)
    sous_categorie_id = Column(Integer)
    nom = Column(Text, nullable=False)
    nom_auto = Column(Boolean)
    unite = Column(Text, nullable=False)
    montant = Column(Float, default=0.0, nullable=False)
    date_entree = Column(Date)
    date_sortie = Column(Date)
    remplace = Column(Text)
    priorite = Column(Boolean)
    ordre = Column(Integer)
    id_html = Column(Text)
    batiment = Column(Boolean)
    bien_fonds = Column(Boolean)
    code = Column(String(8))
    champ_editable = Column(Boolean)
    calcul_auto = Column(Text)


class EmolumentAffaire(Base):
    __tablename__ = "emolument_affaire"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id))
    pente_pc = Column(Integer)
    diff_visibilite_pc = Column(Integer)
    trafic_pc = Column(Integer)
    zi = Column(Float)
    indice_application = Column(Float)
    tva_pc = Column(Float)
    remarque = Column(Text)
    numeros_id = Column(ARRAY(BigInteger))
    facture_type_id = Column(BigInteger)
    utilise = Column(Boolean)


class EmolumentAffaireRepartition(Base):
    __tablename__ = "emolument_affaire_repartition"
    __table_args__ = {"schema": "infolica"}
    emolument_affaire_id = Column(BigInteger, ForeignKey(EmolumentAffaire.id), primary_key=True, nullable=False)
    facture_id = Column(BigInteger, ForeignKey(Facture.id), primary_key=True, nullable=False)
    repartition = Column(Float, nullable=False)


class Emolument(Base):
    __tablename__ = "emolument"
    __table_args__ = {"schema": "infolica"}
    emolument_affaire_id = Column(BigInteger, ForeignKey(EmolumentAffaire.id), primary_key=True)
    tableau_emolument_id = Column(BigInteger, ForeignKey(TableauEmoluments.id), primary_key=True)
    position = Column(Text, primary_key=True)
    prix_unitaire = Column(Float)
    nombre = Column(Float)
    batiment = Column(Integer, primary_key=True)
    batiment_f = Column(Float)
    montant = Column(Float)


class SuiviMandat(Base):
    __tablename__ = "suivi_mandat"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    av_11 = Column(Boolean)  # CREATION DE L’AFFAIRE DANS INFOLICA
    av_12 = Column(Date)  # DATE CREATION DE L’AFFAIRE DANS INFOLICA
    av_21 = Column(Boolean)  # CREATION DE L’AFFAIRE DANSTIMELEAD
    av_31 = Column(Boolean)  # VERIFICATION PAR LE CHEF DE PROJET DE LA MENSURATION OFFICIELLE
    av_32 = Column(BigInteger, ForeignKey(Operateur.id))  # LE CHEF DE PROJET
    av_33 = Column(Date)  # DATE DE LA VERIFICATION PAR LE CHEF DE PROJET
    av_41 = Column(Boolean)  # REPORT DATE PREAVIS SAT OU SEA
    av_51 = Column(Text)  # INFORMATIONS COMPLEMENTAIRES
    pdt_11 = Column(Boolean)  # CONTROLE DES DESIGNATIONS ET DE LA BALANCE
    pdt_12 = Column(Text)  # REMARQUE CONTROLE DES DESIGNATIONS ET DE LA BALANCE
    pdt_21 = Column(Boolean)  # CONTROLE DU TABLEAU DES EMOLUMENTS ET REPORT SUR LA DEMANDE
    pdt_22 = Column(Text)  # REMARQUE CONTROLE DU TABLEAU DES EMOLUMENTS ET REPORT SUR LA DEMANDE
    pdt_31 = Column(Boolean)  # MATERIALISATION DIFFEREE (COPIE DU PLAN DE MUTATION)
    pdt_41 = Column(Boolean)  # CONTROLE DE L'ENREGISTREMENT DE TOUS LES DOCUMENTS (COURRIEL, COURRIER, PREAVIS, PLAN, ETC…)
    pdt_42 = Column(Text)  # REMARQUE CONTROLE DE L'ENREGISTREMENT DE TOUS LES DOCUMENTS (COURRIEL, COURRIER, PREAVIS, PLAN, ETC…)
    ap_11 = Column(Boolean)  # RESPECT DES DIRECTIVES DU SCAT, SAGR OU SERVICE URBANISME
    ap_12 = Column(Text)  # REMARQUE RESPECT DES DIRECTIVES DU SCAT, SAGR OU SERVICE URBANISME
    ap_21 = Column(Boolean)  # STRUCTURE DES REPERTOIRES ET CONTENU
    ap_22 = Column(Text)  # REMARQUE STRUCTURE DES REPERTOIRES ET CONTENU
    ap_31 = Column(Boolean)  # GENERATION DE L’ETAT DESCRIPTIF POUR TERRIS
    ap_32 = Column(BigInteger, ForeignKey(Operateur.id))  # CHEF DE PROJET
    ap_33 = Column(Date)  # DATE GENERATION DE L’ETAT DESCRIPTIF POUR TERRIS
    ap_41 = Column(Boolean)  # CONTROLE DE LA BASE DE DONNEES
    ap_42 = Column(Text)  # REMARQUE CONTROLE DE LA BASE DE DONNEES
    plan_cadastre = Column(Boolean)
    plan_titre = Column(Boolean)
    plan_echelle = Column(Boolean)
    plan_police_bat = Column(Boolean)
    plan_agrandissement_reduction = Column(Boolean)
    plan_no_affaire = Column(Boolean)
    plan_servitude = Column(Boolean)
    plan_num_bf_infolica = Column(Boolean)
    desbal_cadastre = Column(Boolean)
    desbal_titre = Column(Boolean)
    desbal_no_bf = Column(Boolean)
    desbal_no_folio = Column(Boolean)
    desbal_nom_local = Column(Boolean)
    desbal_nom_rue = Column(Boolean)
    desbal_surf_tot = Column(Boolean)
    desbal_surf_nat = Column(Boolean)
    desbal_bat_nat = Column(Boolean)
    desbal_adresse_bat = Column(Boolean)
    desbal_libel_prov = Column(Boolean)
    desbal_libel_remarques_rf = Column(Boolean)
    desbal_libel_obs = Column(Boolean)
    desbal_mat_diff = Column(Boolean)
    desbal_obs_sat = Column(Boolean)
    desbal_num_bf_anciens_nouveaux = Column(Boolean)
    desbal_surf_ancien = Column(Boolean)
    desbal_surf_nouveau = Column(Boolean)
    desbal_ctrl_totaux = Column(Boolean)
    desbal_libel_obs = Column(Boolean)
    geos_couvsol_numerotation_pt_particuliers = Column(Boolean)
    geos_couvsol_numerotation_bat = Column(Boolean)
    geos_couvsol_des_bat = Column(Boolean)
    geos_objdiv_pt_constr_supprimes = Column(Boolean)
    geos_objdiv_geometrie = Column(Boolean)
    geos_objdiv_bat_sout = Column(Boolean)
    geos_bf_rad_mat_diff = Column(Boolean)
    geos_bf_val_pt = Column(Boolean)
    geos_bf_egris_egrid = Column(Boolean)
    geos_bf_statut_valid_juridique = Column(Boolean)
    geos_bf_statut_posimmeuble = Column(Boolean)
    geos_bf_geometrie = Column(Boolean)
    geos_bf_pt_alignes_lim_nat = Column(Boolean)
    geos_servitude_statut_validite = Column(Boolean)
    geos_servitude_libelle = Column(Boolean)
    geos_servitude_no_rs = Column(Boolean)
    geos_servitude_libelle_classe = Column(Boolean)
    geos_servitude_droit_jouissance = Column(Boolean)
    geos_couleur_pastilles = Column(Boolean)
    geos_retarder_validation = Column(Boolean)
    emol_frais_cad = Column(Boolean)
    emol_frais_rf = Column(Boolean)
    emol_frais_division = Column(Boolean)
    emol_frais_materialisation = Column(Boolean)
    preavis_exhaustivite_demandes = Column(Boolean)
    preavis_respect_sat_sagr = Column(Boolean)
    preavis_remarque = Column(Text)
    gen_pdf_travaux = Column(Boolean)
    gen_scan_croquis = Column(Boolean)
    gen_geoportail_attributs = Column(Boolean)
    normes_respect_petits_objects = Column(Boolean)
    normes_bat_couv_digitalises = Column(Boolean)
    pfp3_ctrl_calcul = Column(Boolean)
    pfp3_ctrl_fiabilite = Column(Boolean)
    pfp3_ctrl_coordonnees_geomedia_ltop = Column(Boolean)
    pfp3_protection_symbole_geomedia = Column(Boolean)
    fact_forfait = Column(Boolean)
    fact_adresse_correcte = Column(Boolean)
    fact_lettre_accompagnement = Column(Boolean)
    fact_tva = Column(Boolean)
    fact_coordination_cdf_ne = Column(Boolean)
    fact_domaine_ofrou = Column(Boolean)
    documents_complets = Column(Boolean)
    visa = Column(BigInteger, ForeignKey(Operateur.id))
    date = Column(Date)


class ControleMutation(Base):
    __tablename__ = "controle_mutation"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    terrain_1 = Column(Date)  # Terrain - Levés préliminaires
    terrain_2 = Column(Date)  # Terrain - Matérialisations
    terrain_3 = Column(Date)  # Terrain - Levés
    bureau_1 = Column(Date)  # Bureau - Calculs préliminaires
    bureau_2 = Column(Date)  # Bureau - Calculs définitifs
    bureau_3 = Column(Date)  # Bureau - Calculs spéciaux
    envoi_cl_1 = Column(Date)  # Situation_affaire - Envoi au client
    retour_cl_2 = Column(Date)  # Sitation_affaire - Retour du client
    suivi_1 = Column(Date)  # Suivi - Création de la mutation dans la BD
    suivi_2 = Column(Date)  # Suivi - Contrôles de cohérences e.o.
    suivi_3 = Column(Date)  # Suivi - Production des désignations
    suivi_4 = Column(Date)  # Suivi - Production plan de mutation (papier)
    suivi_5 = Column(Date)  # Suivi - Production plan de mutation (PDF)
    suivi_6 = Column(Date)  # Suivi - Enregistrement de la documentation
    suivi_7 = Column(Date)  # Suivi - État de la mutation "En cours / Libérée"
    suivi_8 = Column(Date)  # Suivi - Tableau des émoluments
    suivi_9 = Column(Date)  # Suivi - Transmission au géomètre cantonal
    suivi_10 = Column(Date)  # Suivi - Transmission au secrétariat
    suivi_11 = Column(Date)  # Suivi - Validation technique de la mutation
    suivi_12 = Column(Date)  # Suivi - Annulation de la mutation
    gen_1 = Column(Boolean)  # Fichier PDF après MPD figurant les travaux en couleur
    gen_2 = Column(Boolean)  # Scan du croquis terrain
    gen_3 = Column(Boolean)  # Attributs corrects dans le suivi (géoportail) : type, statut, personne pré-analyse, personne mesure, remarque
    gen_4 = Column(Boolean)  # Toutes les pastilles sont vertes ou grises
    bf_1 = Column(Boolean)  # Contrôler les numéros des points limites ainsi que la valeur, la prévision et la fiabilité des points sont en adéquation avec le niveau de tolérence de la zone de travail
    bf_2 = Column(Boolean)  # Contrôler dans la table « Bien_fonds => Mise_a_jourBF » qu’il y que les nouveaux biens-fonds créés dans votre affaire et qu'il n'y a pas de biens-fonds sans géométrie
    bf_3 = Column(Boolean)  # Contrôler dans la table « Bien_fonds » que l’attribut « Validation_juridique » est non pour les nouveaux biens-fonds sauf pour les nouveaux DP.
    bf_4 = Column(Boolean)  # Contrôler dans la table « Biens_fonds.PosImmeuble » que les éléments suivants sont corrects (Hali=Center, Vali=Half, Grandeur=Petite.petite).
    cs_1 = Column(Boolean)  # Contrôler les numéros des points particuliers "660" ainsi que la valeur, la précision et la fiabilité des points sont en adéquations avec le niveau de tolérance de la zone de travail.
    cs_2 = Column(Boolean)  # Contrôler dans la table « Couverture_du_sol => Mise_a_jourCS » qu’il y a que les nouvelles surfaces créées dans votre affaire qu'il n'y a pas de surfaces sans géométrie.
    cs_3 = Column(Boolean)  # Contrôler dans la table « Couverture_du_sol => PosNumero_de_batiment » que les éléments suivants sont corrects (Hali=Center, Vali=Base, Grandeur=Petite.tres_petite).
    cs_4 = Column(Boolean)  # Modifier les attributs (raison, identification) dans les propriétés du bâtiment projeté
    cs_5 = Column(Boolean)  # Contrôler la géométrie des EGID (01.01.2012).
    cs_6 = Column(Boolean)  # Réservation des numéros de points particuliers (660).
    cs_7 = Column(Boolean)  # Réservation des numéros de bâtiments.
    cs_8 = Column(Boolean)  # Désignation des bâtiments et bâtiments souterrains.
    cs_9 = Column(Boolean)  # Suppression du point SATAC dans la couche MO édition.
    od_1 = Column(Boolean)  # Tous les points de constructions "760" sont supprimés.
    od_2 = Column(Boolean)  # Contrôler les nouveaux éléments créés dans votre affaire et qu'il n'y a pas d'objets divers sans géométrie.
    od_3 = Column(Boolean)  # Contrôler que les bâtiments souterrains ont les bons numéros et une désignation.
    od_4 = Column(Boolean)  # Modifier les attributs (raison, identification) dans les propriétés du bâtiment projeté
    od_5 = Column(Boolean)  # Contrôler que l'attribut « Objets_divers => SymboleElement_surfacique » est rempli pour les piscines.
    od_6 = Column(Boolean)  # Suppression du point SATAC dans la couche MO édition
    bat_1 = Column(Boolean)  # Contrôler dans la table « Adresses_des_batiments => Mise_a_jourBAT » qu’il y a bien que les nouveaux éléments que vous avez créés dans votre affaire.
    bat_2 = Column(Boolean)  # Contrôler dans la table « Adresses_des_batiments => PosNumero_maison » que les éléments suivants sont corrects (Hali=Center, Vali=Half, Grandeur=Petite.assez_petite).
    bat_3 = Column(Boolean)  # Contrôler que les points adresses sont dans les géométries.
    bat_4 = Column(Boolean)  # Contrôler Bâtiment IMVO (bâtiment sans numéro).
    serv_1 = Column(Boolean)  # Contrôler dans la table « Servitudes => Mise_a_jourSE » qu’il y a bien que les nouveaux éléments que vous avez créés dans votre affaire.
    serv_2 = Column(Boolean)  # Contrôler dans la table « Servitudes => Servitude_surface » ou « Servitudes => Servitude_ligne » ou « Servitudes => Servitude_point » que l’attribut « Validite » est en_projet pour les nouvelles servitudes.
    serv_3 = Column(Boolean)  # Contrôler dans la table « Servitudes => PosNumero_de_servitude » que les éléments suivants sont corrects (Hali=Left, Vali=Base, Grandeur= -).
    nom_1 = Column(Boolean)  # A partir de deux noms locaux pour un bien-fonds vérifier si cela est exact.
    suiv_mut_1 = Column(Boolean)  # Supprimer dans la gestion des mutations les « Topic » qui ne sont pas utilisés.
    suiv_mut_2 = Column(Boolean)  # Mutation "En cours/Libérée".
    div_1 = Column(Boolean)  # Épurations des fichiers dans le répertoire de l’affaire.
    div_2 = Column(Boolean)  # Contrôler que vous avez bien saisi le dernier numéro de point de l’affaire concernée dans le programme « Réservation des numéros ».
    div_3 = Column(Boolean)  # Contrôler rigoureusement les désignations, la balance ainsi que les observations pour le registre foncier.
    visa = Column(BigInteger, ForeignKey(Operateur.id))
    date = Column(Date)


class ControlePPE(Base):
    __tablename__ = "controle_ppe"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    operateur_id = Column(BigInteger, ForeignKey(Operateur.id))
    date = Column(Date)
    gen_1 = Column(Boolean)
    gen_2 = Column(Boolean)
    gen_3 = Column(Boolean)
    gen_4 = Column(Boolean)
    gen_5 = Column(Boolean)
    gen_6 = Column(Boolean)
    gen_7 = Column(Boolean)
    gen_8 = Column(Boolean)
    gen_9 = Column(Boolean)
    gen_remarque = Column(Text)
    dos_a = Column(Boolean)
    dos_b = Column(Boolean)
    dos_c = Column(Boolean)
    dos_d = Column(Boolean)
    dos_e = Column(Boolean)
    dos_f = Column(Boolean)
    dos_g = Column(Boolean)
    dos_h = Column(Boolean)
    dos_remarque = Column(Text)
    jur_a = Column(Boolean)
    jur_b = Column(Boolean)
    jur_c = Column(Boolean)
    jur_d = Column(Boolean)
    jur_remarque = Column(Text)
    psit_a = Column(Boolean)
    psit_b = Column(Boolean)
    psit_c = Column(Boolean)
    psit_d = Column(Boolean)
    psit_e = Column(Boolean)
    psit_f = Column(Boolean)
    psit_g = Column(Boolean)
    psit_h = Column(Boolean)
    psit_i = Column(Boolean)
    psit_j = Column(Boolean)
    psit_k = Column(Boolean)
    psit_l = Column(Boolean)
    psit_m = Column(Boolean)
    psit_n = Column(Boolean)
    psit_o = Column(Boolean)
    psit_p = Column(Boolean)
    psit_q = Column(Boolean)
    psit_r = Column(Boolean)
    psit_s = Column(Boolean)
    psit_t = Column(Boolean)
    psit_u = Column(Boolean)
    psit_v = Column(Boolean)
    psit_w = Column(Boolean)
    psit_x = Column(Boolean)
    psit_y = Column(Boolean)
    psit_z = Column(Boolean)
    psit_remarque = Column(Text)
    pet_a = Column(Boolean)
    pet_b = Column(Boolean)
    pet_c = Column(Boolean)
    pet_d = Column(Boolean)
    pet_e = Column(Boolean)
    pet_f = Column(Boolean)
    pet_g = Column(Boolean)
    pet_h = Column(Boolean)
    pet_i = Column(Boolean)
    pet_j = Column(Boolean)
    pet_k = Column(Boolean)
    pet_l = Column(Boolean)
    pet_m = Column(Boolean)
    pet_n = Column(Boolean)
    pet_o = Column(Boolean)
    pet_p = Column(Boolean)
    pet_q = Column(Boolean)
    pet_r = Column(Boolean)
    pet_remarque = Column(Text)
    cart_a = Column(Boolean)
    cart_b = Column(Boolean)
    cart_c = Column(Boolean)
    cart_d = Column(Boolean)
    cart_e = Column(Boolean)
    cart_f = Column(Boolean)
    cart_g = Column(Boolean)
    cart_h = Column(Boolean)
    cart_i = Column(Boolean)
    cart_j = Column(Boolean)
    cart_remarque = Column(Text)
    uet_a = Column(Boolean)
    uet_b = Column(Boolean)
    uet_c = Column(Boolean)
    uet_d = Column(Boolean)
    uet_e = Column(Boolean)
    uet_f = Column(Boolean)
    uet_g = Column(Boolean)
    uet_h = Column(Boolean)
    uet_i = Column(Boolean)
    uet_j = Column(Boolean)
    uet_k = Column(Boolean)
    uet_l = Column(Boolean)
    uet_m = Column(Boolean)
    uet_n = Column(Boolean)
    uet_o = Column(Boolean)
    uet_p = Column(Boolean)
    uet_q = Column(Boolean)
    uet_r = Column(Boolean)
    uet_s = Column(Boolean)
    uet_t = Column(Boolean)
    uet_u = Column(Boolean)
    uet_v = Column(Boolean)
    uet_w = Column(Boolean)
    uet_x = Column(Boolean)
    uet_y = Column(Boolean)
    uet_z = Column(Boolean)
    uet_aa = Column(Boolean)
    uet_ab = Column(Boolean)
    uet_ac = Column(Boolean)
    uet_ad = Column(Boolean)
    uet_ae = Column(Boolean)
    uet_remarque = Column(Text)
    dup_a = Column(Boolean)
    dup_b = Column(Boolean)
    dup_c = Column(Boolean)
    dup_d = Column(Boolean)
    dup_e = Column(Boolean)
    dup_f = Column(Boolean)
    dup_g = Column(Boolean)
    dup_h = Column(Boolean)
    dup_i = Column(Boolean)
    dup_remarque = Column(Text)
    leg_a = Column(Boolean)
    leg_b = Column(Boolean)
    leg_c = Column(Boolean)
    leg_d = Column(Boolean)
    leg_e = Column(Boolean)
    leg_f = Column(Boolean)
    leg_g = Column(Boolean)
    leg_h = Column(Boolean)
    leg_i = Column(Boolean)
    leg_j = Column(Boolean)
    leg_k = Column(Boolean)
    leg_l = Column(Boolean)
    leg_m = Column(Boolean)
    leg_n = Column(Boolean)
    leg_o = Column(Boolean)
    leg_p = Column(Boolean)
    leg_q = Column(Boolean)
    leg_r = Column(Boolean)
    leg_s = Column(Boolean)
    leg_t = Column(Boolean)
    leg_u = Column(Boolean)
    leg_v = Column(Boolean)
    leg_w = Column(Boolean)
    leg_x = Column(Boolean)
    leg_y = Column(Boolean)
    leg_remarque = Column(Text)
    balsurf_a = Column(Boolean)
    balsurf_b = Column(Boolean)
    balsurf_c = Column(Boolean)
    balsurf_d = Column(Boolean)
    balsurf_remarque = Column(Text)


class ControleGeometre(Base):
    __tablename__ = "controle_geometre"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    operateur_id = Column(BigInteger, ForeignKey(Operateur.id))
    date = Column(Date)
    remarque = Column(Text)
    info_gen_adresses = Column(Integer, default=-1)
    info_gen_referencement_affaire = Column(Integer, default=-1)
    info_gen_dossier_complet = Column(Integer, default=-1)
    info_gen_numeros_recuperes = Column(Integer, default=-1)
    asp_jur_respect_preavis = Column(Integer, default=-1)
    asp_jur_bf_existent_rf = Column(Integer, default=-1)
    asp_jur_no_reserves_no_utilises = Column(Integer, default=-1)
    asp_jur_acces_dp = Column(Integer, default=-1)
    asp_jur_servitudes = Column(Integer, default=-1)
    asp_jur_no_etat_juridique_bf_base = Column(Integer, default=-1)
    asp_jur_plan_sit_plan_etage = Column(Integer, default=-1)
    asp_jur_plan_mention_partiellement = Column(Integer, default=-1)
    asp_jur_nb_doc_legende = Column(Integer, default=-1)
    asp_jur_tampons_corrects = Column(Integer, default=-1)
    fact_repartition_destinataires = Column(Integer, default=-1)
    fact_montant_servitudes = Column(Integer, default=-1)
    fact_no_affaire = Column(Integer, default=-1)
    fact_libelles = Column(Integer, default=-1)
    fact_prix_unitaire_prix_total = Column(Integer, default=-1)
    fact_prix_pfp = Column(Integer, default=-1)
    fact_prix_pl = Column(Integer, default=-1)
    fact_destinataires_enveloppes_coherents = Column(Integer, default=-1)
    fact_lettre_a = Column(Integer, default=-1)
    fact_remarque_devis_facture = Column(Integer, default=-1)
    fact_contenu_emolument = Column(Integer, default=-1)
    coherence_doc_cadastre_bf_titre = Column(Integer, default=-1)
    ctrl_juridique_coherence_doc_cadastre_bf_titre = Column(Integer, default=-1)
    coherence_doc_reunion_bat_egid = Column(Integer, default=-1)
    coherence_doc_nb_pts_factues = Column(Integer, default=-1)
    coherence_doc_date = Column(Integer, default=-1)
    coherence_doc_bat_num = Column(Integer, default=-1)
    balance_avancement_saisie_servitudes = Column(Integer, default=-1)
    balance_surfaces_ancien_rf = Column(Integer, default=-1)
    balance_somme_surfaces = Column(Integer, default=-1)
    balance_surface_bf_base_creation_ddp = Column(Integer, default=-1)
    balance_surface_ddp = Column(Integer, default=-1)
    etat_desc_provenances = Column(Integer, default=-1)
    etat_desc_surface_totale_bf = Column(Integer, default=-1)
    etat_desc_somme_surfaces_natures = Column(Integer, default=-1)
    etat_desc_nom_rue = Column(Integer, default=-1)
    mat_diff_infos = Column(Integer, default=-1)
    courrier_destinataires_enveloppes_coherents = Column(Integer, default=-1)
    courrier_lettre_a = Column(Integer, default=-1)
    des_provenances = Column(Integer, default=-1)
    des_surface_totale_bf = Column(Integer, default=-1)
    des_somme_surfaces_natures = Column(Integer, default=-1)
    des_nb_documents = Column(Integer, default=-1)
    des_tampon_geom_date = Column(Integer, default=-1)
    des_tampon_duplicata_date = Column(Integer, default=-1)
    des_tampon_copie_geom_date = Column(Integer, default=-1)
    des_mention_sans_frais = Column(Integer, default=-1)
    des_nom_proprietaire = Column(Integer, default=-1)
    des_surface_bf_mo_rf = Column(Integer, default=-1)
    des_somme_surfaces_ed = Column(Integer, default=-1)
    des_designation_bat = Column(Integer, default=-1)
    des_tampon_geom_date_initiale = Column(Integer, default=-1)
    des_tampon_modifie_date = Column(Integer, default=-1)
    des_tampon_vise_date = Column(Integer, default=-1)
    plan_no_bf = Column(Integer, default=-1)
    plan_tampon_geom_date = Column(Integer, default=-1)
    plan_tampon_duplicata_date = Column(Integer, default=-1)
    plan_tampon_copie_geom_date = Column(Integer, default=-1)
    plan_tampon_geom_date_initiale = Column(Integer, default=-1)
    plan_tampon_modifie_date = Column(Integer, default=-1)
    plan_servitudes = Column(Integer, default=-1)
    plan_tampon_vise_date = Column(Integer, default=-1)
    lettres_no_affaire = Column(Integer, default=-1)
    lettres_saisie_manuelle = Column(Integer, default=-1)
    lettres_paragraphe_ppe = Column(Integer, default=-1)
    lettres_lettre_cad_office = Column(Integer, default=-1)
    req_saisie_manuelle = Column(Integer, default=-1)
    devis_fact_remarques = Column(Integer, default=-1)
    devis_fact_no_emolument = Column(Integer, default=-1)
    devis_fact_montant_rf = Column(Integer, default=-1)


class ControleGeometre_old(Base):
    __tablename__ = "controle_geometre_old"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    check_1 = Column(Boolean)  # Nom du cadastre et n° de bien-fonds corrects (cf extrait RF) et identiques sur tous les documents
    check_2 = Column(Boolean)  # Tous les biens-fonds concernés existent au registre foncier (d’après l’extrait RF), sinon ajouter une observation concernant l’ordre de dépôt des dossiers au RF
    check_3 = Column(Boolean)  # Vérifier le bien-fondé des servitudes ainsi que leur faisabilité
    check_4 = Column(Boolean)  # Sommes des surfaces de l’état descriptif
    check_5 = Column(Boolean)  # Les surfaces « ancien état » de la balance correspondent aux surfaces RF
    check_6 = Column(Boolean)  # Sommes des surfaces de la balance
    check_7 = Column(Boolean)  # Les éventuelles différences de m2 sont bien expliquées (a priori, pas de correction des surfaces des nouveaux biens-fonds)
    check_8 = Column(Boolean)  # Les provenances sont cohérentes
    check_9 = Column(Boolean)  # La surface des DDP ne change pas entre l’ancien état et le nouvel état, sinon mettre un commentaire concernant le changement de surface du DDP
    check_10 = Column(Boolean)  # BB a inscrit le montant pour le report des servitudes dans le fichier excel
    check_11 = Column(Boolean)  # Les titres sont cohérents sur tous les documents
    check_12 = Column(Boolean)  # Le dossier respecte les indications du SCAT / SAGR / SENE
    check_13 = Column(Boolean)  # BB a pris en compte les indications du SCAT / SAGR / SENE
    check_14 = Column(Boolean)  # Chaque nouveau BF ait un accès au DP
    check_15 = Column(Boolean)  # Nom du cadastre et n° de bien-fonds corrects (cf extrait RF) et identiques sur tous les documents
    check_16 = Column(Boolean)  # Les titres sont cohérents sur tous les documents
    check_17 = Column(Boolean)  # Cohérence des provenances
    check_18 = Column(Boolean)  # Nombre de documents: « fait en x plans, x désignations et x formules de report des servitude »
    check_19 = Column(Boolean)  # Tampon(s) et date(s) sur la dernière feuille
    check_20 = Column(Boolean)  # Mention « sans frais » indiquée le cas échéant (surtout changement dans ses natures)
    check_21 = Column(Boolean)  # Le n° du BF est visible sur le plan
    check_22 = Column(Boolean)  # Tampon(s) et date(s)
    check_23 = Column(Boolean)  # Titre de la facture
    check_24 = Column(Boolean)  # Quantité et désignation (n° BF + cadastre) des articles facturés
    check_25 = Column(Boolean)  # Prix unitaire des articles facturés (cf fichier excel)
    check_26 = Column(Boolean)  # Si le destinataire de la facture est différent de celui des documents, vérifier que l’enveloppe contenant les documents porte la bonne adresse et qu’il y a 2 enveloppes
    check_27 = Column(Boolean)  # Lettre A sur l’enveloppe (quand pour acte notarié)
    check_28 = Column(Boolean)  # Présence de la lettre d’information à propos de la cadastration d’office
    check_29 = Column(Boolean)  # Eléments saisis manuellement (cf exemples)
    check_30 = Column(Boolean)  # Eléments issus d’Infolica (cf exemples)
    check_31 = Column(Boolean)  # Paragraphes spécifiques si une PPE et constituée sur le fond de base ou si une mention de « Constitution de PPE avant la construction du bâtiment » figure
    check_32 = Column(Boolean)  # Eléments saisis manuellement (cf exemples)
    check_33 = Column(Boolean)  # Chaque bâtiment a un numéro
    check_34 = Column(Boolean)  # Vérifier que le nom du propriétaire est entier
    check_35 = Column(Boolean)  # La surface du bien-fonds est la même que celle inscrite au RF
    check_36 = Column(Boolean)  # Vérifier les sommes des surfaces de l’état descriptif
    check_37 = Column(Boolean)  # Chaque bâtiment a un numéro
    check_38 = Column(Boolean)  # Pertinence de la désignation de bâtiment
    check_39 = Column(Boolean)  # Phrase « DUPLICATA du plan du … »
    check_40 = Column(Boolean)  # Phrase « DUPLICATA du plan du … »
    check_41 = Column(Boolean)  # Contrôle de l’indication « Visa » ou « Modification »
    check_42 = Column(Boolean)  # Contrôle de l’indication « Visa » ou « Modification »
    check_43 = Column(Boolean)  # contrôler si la servitude telle qu’elle est prévue est pertinente et possible. Il est possible qu’il faille diviser les géométries des servitudes pour représenter les différentes utilisations.
    check_44 = Column(Boolean)  # Le nombre de points est le même que sur le plan
    check_45 = Column(Boolean)  # Le montant est correct (~300.- par PL)
    check_46 = Column(Boolean)  # Le nombre de points est le même que sur le plan
    check_47 = Column(Boolean)  # Le montant est correct (~ 380.- par PFP)
    check_48 = Column(Boolean)  # Adresses (commande, envoi, facturation)
    check_49 = Column(Boolean)  # Référencement géographique
    check_50 = Column(Boolean)  # N° de biens-fonds réservés = n° de biens-fonds utilisés
    check_51 = Column(Boolean)  # Si plusieurs destinataires, la répartition est indiquée (devis et factures)
    check_52 = Column(Boolean)  # Indication sur l'avancement de la saisie des servitudes
    check_53 = Column(Boolean)  # Surface du bien-fonds de base ne change pas lors de la création d'un DDP
    check_54 = Column(Boolean)  # Surface totale de chaque bien-fonds
    check_55 = Column(Boolean)  # Nom de rue pour un bien-fonds non construit en zone à bâtir
    check_56 = Column(Boolean)  # Informations concernant la Mat. Diff. (immeuble, facture, désignation)
    check_57 = Column(Boolean)  # N° d'affaire
    check_58 = Column(Boolean)  # Surface totale de chaque bien-fonds
    check_59 = Column(Boolean)  # Sommes des surfaces des natures pour chaque bien-fonds
    check_60 = Column(Boolean)  # Référencement géographique de l'affaire
    check_61 = Column(Boolean)  # Remarque(s) de la rubrique "Devis et factures"
    check_62 = Column(Boolean)  # Dossier complet (formule de légende, plan de situation, plans d'étage, coupes, plans de façade)
    check_63 = Column(Boolean)  # N° et état juridique du BF de base
    check_64 = Column(Boolean)  # Informations cohérentes entre plan de situation et plans d'étage
    check_65 = Column(Boolean)  # Nombres de documents indiqués sur la formule de légende
    check_66 = Column(Boolean)  # Contenu de la facture
    operateur_id = Column(BigInteger, ForeignKey(Operateur.id))
    date = Column(Date)
    remarque = Column(Text)


class NumeroType(Base):
    __tablename__ = "numero_type"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)
    ordre = Column(BigInteger)


class NumeroEtat(Base):
    __tablename__ = "numero_etat"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class Numero(Base):
    __tablename__ = "numero"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cadastre_id = Column(BigInteger, ForeignKey(Cadastre.id), nullable=False)
    type_id = Column(BigInteger, ForeignKey(NumeroType.id), nullable=False)
    numero = Column(BigInteger, nullable=False)
    suffixe = Column(Text)
    etat_id = Column(BigInteger, ForeignKey(NumeroEtat.id), nullable=False)
    no_access = Column(Text)

    UniqueConstraint(cadastre_id, numero)


class ReservationNumerosMO(Base):
    __tablename__ = "reservation_numeros"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    cadastre_id = Column(BigInteger, ForeignKey(Cadastre.id), nullable=False)
    plan_id = Column(Text)
    plan = Column(Integer)
    type_id = Column(BigInteger, ForeignKey(NumeroType.id), nullable=False)
    numero_de = Column(BigInteger)
    numero_a = Column(BigInteger)
    date = Column(Date, default=datetime.datetime.utcnow)
    remarque = Column(Text)
    operateur_id = Column(BigInteger, ForeignKey(Operateur.id), nullable=False)
    affaire_no_access = Column(Text)


class NumeroEtatHisto(Base):
    __tablename__ = "numero_etat_histo"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    numero_id = Column(BigInteger, ForeignKey(Numero.id), nullable=False)
    numero_etat_id = Column(BigInteger, ForeignKey(NumeroEtat.id), nullable=False)
    date = Column(Date, default=datetime.datetime.utcnow, nullable=False)


class NumeroDiffere(Base):
    __tablename__ = "numero_differe"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    numero_id = Column(BigInteger, ForeignKey(Numero.id), nullable=False)
    date_entree = Column(Date, default=datetime.datetime.utcnow, nullable=False)
    date_sortie = Column(Date)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id))
    req_radiation = Column(Boolean)
    req_ref = Column(Text)
    date_controle = Column(Date)


class NumeroRelationType(Base):
    __tablename__ = "numero_relation_type"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class NumeroRelation(Base):
    __tablename__ = "numero_relation"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    numero_id_base = Column(Integer, ForeignKey(Numero.id), nullable=False)
    numero_id_associe = Column(Integer, ForeignKey(Numero.id), nullable=False)
    relation_type_id = Column(BigInteger, ForeignKey(NumeroRelationType.id), nullable=False)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id))

    UniqueConstraint(numero_id_base, numero_id_associe, relation_type_id, affaire_id)


class AffaireNumeroType(Base):
    __tablename__ = "affaire_numero_type"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class AffaireNumero(Base):
    __tablename__ = "affaire_numero"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    numero_id = Column(BigInteger, ForeignKey(Numero.id), nullable=False)
    type_id = Column(BigInteger, ForeignKey(AffaireNumeroType.id))  # , nullable=False)
    actif = Column(Boolean, default=True, nullable=False)
    affaire_destination_id = Column(BigInteger, ForeignKey(Affaire.id))


class PreavisType(Base):
    __tablename__ = "preavis_type"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class Preavis(Base):
    __tablename__ = "preavis"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    service_id = Column(BigInteger, ForeignKey(Service.id), nullable=False)
    preavis_type_id = Column(BigInteger, ForeignKey(PreavisType.id))
    operateur_sgrf_id = Column(BigInteger, ForeignKey(Operateur.id))
    operateur_service_id = Column(BigInteger, ForeignKey(Operateur.id))
    date_demande = Column(Date, default=datetime.datetime.utcnow, nullable=False)
    date_reponse = Column(Date)
    remarque = Column(Text)
    etape = Column(Text)


class PreavisDecision(Base):
    __tablename__ = "preavis_decision"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    preavis_id = Column(BigInteger, ForeignKey(Preavis.id), nullable=False)
    preavis_type_id = Column(BigInteger, ForeignKey(PreavisType.id))
    operateur_service_id = Column(BigInteger, ForeignKey(Operateur.id))
    remarque_contexte = Column(Text)
    remarque_limite_fictive_gabarits = Column(Text)
    remarque_transfert_droit_batir = Column(Text)
    remarque_stationnement_art29 = Column(Text)
    remarque_autre = Column(Text)
    date = Column(Date)
    definitif = Column(Boolean)
    version = Column(Integer)


class PreavisRemarque(Base):
    __tablename__ = "preavis_remarque"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    preavis_id = Column(BigInteger, ForeignKey(Preavis.id), nullable=False)
    remarque = Column(Text, nullable=False)
    operateur_id = Column(BigInteger, ForeignKey(Operateur.id))
    date = Column(Date, default=datetime.datetime.utcnow, nullable=False)
    lu_operateur_id = Column(BigInteger, ForeignKey(Operateur.id))


class PreavisGlossaire(Base):
    __tablename__ = "preavis_glossaire"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    service_id = Column(BigInteger, ForeignKey(Service.id), nullable=False)
    ordre = Column(Integer)
    titre = Column(Text, nullable=False)
    texte = Column(Text, nullable=False)
    chapitre = Column(String(40))


class GeosBalance(Base):
    __tablename__ = "geos_balance"
    __table_args__ = {"schema": "infolica"}
    idobj = Column(String(40), primary_key=True)
    base = Column(String(50))
    numero_new = Column(String(50))
    cad_new = Column(Integer)
    parcel_new = Column(String(20))
    superficie_new = Column(Integer)
    numero_old = Column(String(50))
    cad_old = Column(Integer)
    parcel_old = Column(String(20))
    superficie_old = Column(Integer)
    superficie_partie = Column(Integer)
    mutation = Column(String(50))
    mutation_desc = Column(String(200))
    egrid_old = Column(String(50))
    gid_geom_new = Column(String(50))
    gid_numero_new = Column(String(50))
    gid_geom_old = Column(String(50))
    gid_numero_old = Column(String(50))
    gid_mutation = Column(String(50))
    geom = Column(Geometry("POINT"))


class EtapeMailer(Base):
    __tablename__ = "etape_mailer"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    etape_id = Column(BigInteger, ForeignKey(AffaireEtapeIndex.id), nullable=False)
    operateur_id = Column(BigInteger, ForeignKey(Operateur.id), nullable=False)
    sendmail = Column(Boolean)


class NotesMAJ(Base):
    __tablename__ = "notes_maj"
    __table_args__ = {"schema": "infolica"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    operateur_id = Column(BigInteger, ForeignKey(Operateur.id), nullable=False)
    version = Column(Text, nullable=False)
    titre = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    date = Column(Date, nullable=False)
    delai = Column(Date, nullable=False)


class ControleEtape(Base):
    __tablename__ = "controle_etape"
    __table_args__ = {"schema": "infolica"}
    nom = Column(String(40), primary_key=True)
    etape_id = Column(BigInteger, ForeignKey(AffaireEtapeIndex.id))
    force = Column(String(15))
    detail = Column(Text)


class ControleEtapeTypeAffaire(Base):
    __tablename__ = "controle_etape_type_affaire"
    __table_args__ = {"schema": "infolica"}
    affaire_type_id = Column(BigInteger, ForeignKey(AffaireType.id), primary_key=True)
    controle_etape_nom = Column(String(40), ForeignKey(ControleEtape.nom), primary_key=True)


# ======================== SCHEMA WEBSERVICES ========================

class AccessibiliteService(Base):
    __tablename__ = "accessibilite_service"
    __table_args__ = {"schema": "webservices"}
    id = Column(BigInteger, primary_key=True)
    service = Column(Text, nullable=False)
    relpath = Column(Text, nullable=False)
    interval = Column(Interval, nullable=False)


class AccessibiliteAffaire(Base):
    __tablename__ = "accessibilite_affaire"
    __table_args__ = {"schema": "webservices"}
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), primary_key=True)
    service_id = Column(BigInteger, ForeignKey(AccessibiliteService.id), primary_key=True)
    token = Column(Text)
    token_set = Column(Date, nullable=False)


# ======================== VUES ========================
# Ajouter l'information 'info': dict(is_view=True) aux vues
# pour qu'elles ne soient pas prises en compte dans les migrations par Alembic

class VNumeros(Base):
    __tablename__ = "v_numeros"
    __table_args__ = {"schema": "infolica", "info": dict(is_view=True)}
    id = Column(BigInteger, primary_key=True)
    cadastre = Column(Text)
    cadastre_id = Column(BigInteger)
    numero = Column(BigInteger)
    numero_sitn = Column(Text)
    suffixe = Column(Text)
    etat = Column(Text)
    etat_id = Column(BigInteger)
    type_numero = Column(Text)
    type_numero_id = Column(BigInteger)
    diff_id = Column(Date)
    diff_entree = Column(Date)
    diff_sortie = Column(Date)
    diff_controle = Column(Date)
    diff_affaire_id = Column(BigInteger)
    diff_req_radiation = Column(Boolean)
    diff_operateur_id = Column(BigInteger)
    diff_operateur_nom = Column(Text)
    diff_operateur_prenom = Column(Text)
    diff_operateur_initiales = Column(Text)
    diff_req_ref = Column(Text)


class VNumerosAffaires(Base):
    __tablename__ = "v_numeros_affaires"
    __table_args__ = {"schema": "infolica", "info": dict(is_view=True)}
    id = Column(BigInteger, primary_key=True)
    numero_id = Column(BigInteger)
    affaire_id = Column(BigInteger)
    affaire_numero_type_id = Column(BigInteger)
    affaire_numero_actif = Column(Boolean)
    affaire_destination_id = Column(BigInteger)
    affaire_nom = Column(Text)
    affaire_type = Column(Text)
    affaire_date_ouverture = Column(Date)
    affaire_date_envoi = Column(Date)
    affaire_date_validation = Column(Date)
    affaire_date_cloture = Column(Date)
    affaire_information = Column(Text)
    numero_cadastre = Column(Text)
    numero_cadastre_id = Column(BigInteger)
    numero_type = Column(Text)
    numero_type_id = Column(BigInteger)
    numero = Column(BigInteger)
    numero_suffixe = Column(Text)
    numero_etat = Column(Text)
    numero_etat_id = Column(BigInteger)
    numero_diff_id = Column(Date)
    numero_diff_entree = Column(Date)
    numero_diff_sortie = Column(Date)
    numero_diff_controle = Column(Date)
    numero_base_id = Column(BigInteger)
    numero_base_type = Column(Text)
    numero_base = Column(BigInteger)
    numero_base_suffixe = Column(Text)
    numero_base_etat = Column(Text)
    numero_base_etat_id = Column(Text)
    numero_base_sitn = Column(Text)
    affaire_numero_type = Column(Text)
    numero_sitn = Column(Text)


class VAffaire(Base):
    __tablename__ = "v_affaires"
    __table_args__ = {"schema": "infolica", "info": dict(is_view=True)}
    id = Column(BigInteger, primary_key=True)
    no_access = Column(Text)
    nom = Column(Text)
    client_commande_id = Column(BigInteger)
    client_commande_type_id = Column(BigInteger)
    client_commande_type = Column(Text)
    client_commande_entreprise = Column(Text)
    client_commande_titre = Column(Text)
    client_commande_nom = Column(Text)
    client_commande_prenom = Column(Text)
    client_commande_complement = Column(Text)
    client_commande_adresse = Column(Text)
    client_commande_co = Column(Text)
    client_commande_npa = Column(Text)
    client_commande_localite = Column(Text)
    client_commande_tel_fixe = Column(Text)
    client_commande_tel_portable = Column(Text)
    client_commande_fax = Column(Text)
    client_commande_mail = Column(Text)
    client_commande_no_sap = Column(Text)
    client_commande_no_bdp_bdee = Column(Text)
    client_envoi_id = Column(BigInteger)
    client_envoi_type_id = Column(BigInteger)
    client_envoi_type = Column(Text)
    client_envoi_entreprise = Column(Text)
    client_envoi_titre = Column(Text)
    client_envoi_nom = Column(Text)
    client_envoi_prenom = Column(Text)
    client_envoi_complement = Column(Text)
    client_envoi_co = Column(Text)
    client_envoi_adresse = Column(Text)
    client_envoi_npa = Column(Text)
    client_envoi_localite = Column(Text)
    client_envoi_tel_fixe = Column(Text)
    client_envoi_tel_portable = Column(Text)
    client_envoi_fax = Column(Text)
    client_envoi_mail = Column(Text)
    client_envoi_no_sap = Column(Text)
    client_envoi_no_bdp_bdee = Column(Text)
    technicien_id = Column(BigInteger)
    technicien_nom = Column(Text)
    technicien_prenom = Column(Text)
    technicien_initiales = Column(Text)
    type_affaire = Column(Text)
    cadastre = Column(Text)
    information = Column(Text)
    date_ouverture = Column(Date)
    date_validation = Column(Date)
    date_envoi = Column(Date)
    date_cloture = Column(Date)
    localisation_e = Column(Float)
    localisation_n = Column(Float)
    cadastre_id = Column(BigInteger)
    type_id = Column(BigInteger)
    vref = Column(Text)
    chemin = Column(Text)
    reservation_numeros_types_id = Column(ARRAY(BigInteger))
    modif_affaire_type_id_vers = Column(ARRAY(BigInteger))
    modification_type_id = Column(BigInteger)
    modification_type = Column(Text)
    modification_affaire_id_mere = Column(BigInteger)
    preavis_scat_date_demande = Column(Date)
    preavis_scat_date_reponse = Column(Date)
    preavis_sagr_date_demande = Column(Date)
    preavis_sagr_date_reponse = Column(Date)
    preavis_sene_date_demande = Column(Date)
    preavis_sene_date_reponse = Column(Date)
    preavis_rf_date_demande = Column(Date)
    preavis_rf_date_reponse = Column(Date)
    etape_id = Column(BigInteger)
    etape = Column(Text)
    etape_datetime = Column(DateTime)
    etape_remarque = Column(Text)
    etape_operateur_id = Column(BigInteger)
    etape_operateur_nom = Column(Text)
    etape_operateur_prenom = Column(Text)
    etape_priorite = Column(Integer)
    etape_ordre = Column(BigInteger)
    abandon = Column(Boolean)
    urgent = Column(Boolean)
    urgent_echeance = Column(Date)
    attribution = Column(Text)
    geos_retarder_validation = Column(Boolean)


class VEnvois(Base):
    __tablename__ = "v_envois"
    __table_args__ = {"schema": "infolica", "info": dict(is_view=True)}
    id = Column(BigInteger, primary_key=True)
    affaire_id = Column(BigInteger)
    affaire_nom = Column(Text)
    client_id = Column(BigInteger)
    client_entreprise = Column(Text)
    client_titre = Column(Text)
    client_nom = Column(Text)
    client_prenom = Column(Text)
    client_complement = Column(Text)
    envoi_type_id = Column(BigInteger)
    envoi_type = Column(Text)
    date = Column(Date)


class VEtapesAffaires(Base):
    __tablename__ = "v_etapes_affaires"
    __table_args__ = {"schema": "infolica", "info": dict(is_view=True)}
    id = Column(BigInteger, primary_key=True)
    affaire_id = Column(BigInteger)
    etape_id = Column(BigInteger, primary_key=True)
    etape = Column(Text)
    remarque = Column(Text)
    datetime = Column(DateTime)
    operateur_id = Column(BigInteger)
    operateur_nom = Column(Text)
    operateur_prenom = Column(Text)
    operateur_initiales = Column(Text)
    etape_ordre = Column(BigInteger)
    etape_priorite = Column(Integer)
    next_operateur_id = Column(BigInteger)
    next_operateur_nom = Column(Text)
    next_operateur_prenom = Column(Text)
    next_operateur_initiales = Column(Text)
    next_remarque = Column(Text)
    next_datetime = Column(DateTime)
    next_etape_id = Column(BigInteger)
    next_nb_jours_hors_sgrf = Column(Integer)


class VAffairesPreavis(Base):
    __tablename__ = "v_affaires_preavis"
    __table_args__ = {"schema": "infolica", "info": dict(is_view=True)}
    id = Column(BigInteger, primary_key=True)
    affaire_id = Column(BigInteger)
    service = Column(Text)
    service_id = Column(BigInteger)
    preavis = Column(Text)
    preavis_type_id = Column(BigInteger)
    date_demande = Column(Date)
    date_reponse = Column(Date)
    remarque = Column(Text)
    etape = Column(Text)
    operateur_sgrf_id = Column(BigInteger)
    operateur_sgrf_prenom = Column(Text)
    operateur_sgrf_nom = Column(Text)
    operateur_service_id = Column(BigInteger)
    operateur_service_prenom = Column(Text)
    operateur_service_nom = Column(Text)


class VTableauBord(Base):
    __tablename__ = "v_tableau_de_bord"
    __table_args__ = {"schema": "infolica", "info": dict(is_view=True)}
    affaire_id = Column(BigInteger, primary_key=True)
    affaire_nom = Column(Text)
    delai = Column(Integer)
    client_entreprise = Column(Text)
    client_titre = Column(Text)
    client_nom = Column(Text)
    client_prenom = Column(Text)
    affaire_type = Column(Text)
    chef_nom = Column(Text)
    chef_prenom = Column(Text)
    technicien_nom = Column(Text)
    technicien_prenom = Column(Text)
    information = Column(Text)
    cadastre = Column(Text)
    etape = Column(Text)


class VEmolumentsFactures(Base):
    __tablename__ = "v_emoluments_factures"
    __table_args__ = {"schema": "infolica", "info": dict(is_view=True)}
    facture_id = Column(BigInteger, primary_key=True)
    domaine = Column(Text)
    categorie = Column(Text)
    sous_categorie = Column(Text)
    nom = Column(Text, primary_key=True)
    unite = Column(Text)
    prix_unitaire = Column(Text)
    nombre = Column(Integer, primary_key=True)
    facteur_correctif = Column(Float)
    batiment = Column(Text, primary_key=True)
    montant = Column(Float)


class VNumerosRelations(Base):
    __tablename__ = "v_numeros_relations"
    __table_args__ = {"schema": "infolica", "info": dict(is_view=True)}
    affaire_id = Column(BigInteger)
    numero_relation_id = Column(BigInteger, primary_key=True)
    numero_base_id = Column(BigInteger)
    numero_base_cadastre_id = Column(BigInteger)
    numero_base_cadastre = Column(Text)
    numero_base_type_id = Column(BigInteger)
    numero_base_type = Column(Text)
    numero_base = Column(BigInteger)
    numero_base_suffixe = Column(Text)
    numero_base_etat_id = Column(BigInteger)
    numero_base_etat = Column(Text)
    numero_associe_id = Column(BigInteger)
    numero_associe_cadastre_id = Column(BigInteger)
    numero_associe_cadastre = Column(Text)
    numero_associe_type_id = Column(BigInteger)
    numero_associe_type = Column(Text)
    numero_associe = Column(BigInteger)
    numero_associe_suffixe = Column(Text)
    numero_associe_etat_id = Column(BigInteger)
    numero_associe_etat = Column(Text)
    numero_relation_type_id = Column(BigInteger)
    numero_relation_type = Column(Text)


class VDocumentsAffaires(Base):
    __tablename__ = "v_documents_affaires"
    __table_args__ = {"schema": "infolica", "info": dict(is_view=True)}
    id = Column(BigInteger, primary_key=True)
    nom = Column(Text)
    chemin = Column(Text)
    affaire_id = Column(BigInteger)
    type_id = Column(BigInteger)
    type_doc = Column(Text)


class VFactures(Base):
    __tablename__ = "v_factures"
    __table_args__ = {"schema": "infolica", "info": dict(is_view=True)}
    id = Column(BigInteger, primary_key=True)
    affaire_id = Column(BigInteger)
    affaire_vref = Column(Text)
    type_id = Column(BigInteger)
    sap = Column(Text)
    client_type_id = Column(BigInteger)
    client_type = Column(Text)
    client_id = Column(BigInteger)
    client_entreprise = Column(Text)
    client_titre = Column(Text)
    client_nom = Column(Text)
    client_prenom = Column(Text)
    client_co = Column(Text)
    client_adresse = Column(Text)
    client_npa = Column(Text)
    client_localite = Column(Text)
    client_case_postale = Column(Text)
    client_tel_fixe = Column(Text)
    client_fax = Column(Text)
    client_tel_portable = Column(Text)
    client_mail = Column(Text)
    client_entree = Column(Date)
    client_sortie = Column(Date)
    client_no_sap = Column(Text)
    client_no_bdp_bdee = Column(Text)
    client_complement = Column(Text)
    client_premiere_ligne = Column(Text)
    montant_mo = Column(Float)
    montant_mat_diff = Column(Float)
    montant_rf = Column(Float)
    montant_tva = Column(Float)
    montant_total = Column(Float)
    date = Column(Date)
    remarque = Column(Text)
    numeros = Column(ARRAY(BigInteger))
    emolument_affaire_id = Column(BigInteger)


class VReservationNumerosMO(Base):
    __tablename__ = "v_reservation_numeros_mo"
    __table_args__ = {"schema": "infolica", "info": dict(is_view=True)}
    id = Column(BigInteger, primary_key=True)
    affaire_id = Column(BigInteger)
    cadastre_id = Column(BigInteger)
    cadastre = Column(Text)
    type_id = Column(BigInteger)
    type_numero = Column(Text)
    numero_de = Column(BigInteger)
    numero_a = Column(BigInteger)
    date = Column(Date)
    remarque = Column(Text)
    operateur_id = Column(BigInteger)
    operateur_nom = Column(Text)
    operateur_prenom = Column(Text)
    plan_id = Column(String(length=40))
    plan_id2 = Column(String(length=20))
    plan_no = Column(String(length=5))
    plan_type = Column(String(length=15))
    plan_datemev = Column(String(length=25))
    plan_statut = Column(String(length=40))
    plan_echelle = Column(Integer)
    plan_idorplan = Column(String(length=40))
    plan_idrepplan = Column(String(length=40))
    plan_base = Column(String(length=50))


class VPlan(Base):
    __tablename__ = "v_plans_mo"
    __table_args__ = {"schema": "infolica", "info": dict(is_view=True)}
    idobj = Column(Text, primary_key=True)
    id_obj2 = Column(Text)
    cadastre_id = Column(BigInteger)
    cadastre = Column(Text)
    planno = Column(Integer)
    typlan = Column(Text)
    datmev = Column(Text)
    statut = Column(Text)
    echell = Column(Integer)
    idborplan = Column(Text)
    idrepplan = Column(Text)
    base = Column(Text)


class VProchainNumeroDisponible(Base):
    __tablename__ = "v_prochain_numero_disponible"
    __table_args__ = {"schema": "infolica", "info": dict(is_view=True)}
    cadastre_id = Column(BigInteger, primary_key=True)
    cadastre = Column(Text)
    plan = Column(Integer, primary_key=True)
    numero_type_id = Column(BigInteger, primary_key=True)
    numero_type = Column(Text)
    prochain_numero = Column(BigInteger)
