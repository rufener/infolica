from sqlalchemy import (
    Column,
    Index,
    Integer,
    BigInteger,
    Float,
    Text,
    Date,
    Boolean,
    ARRAY,
    ForeignKey,
    UniqueConstraint,
)

import datetime
from .constant import Constant
from .meta import Base


class Operateur(Base):
    __tablename__ = 'operateur'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)
    prenom = Column(Text, nullable=False)
    login = Column(Text)  # , nullable=False)
    responsable = Column(Boolean, default=False, nullable=False)
    entree = Column(Date, default=datetime.datetime.utcnow, nullable=False)
    sortie = Column(Date)


class Cadastre(Base):
    __tablename__ = 'cadastre'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class ClientType(Base):
    __tablename__ = 'client_type'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class Client(Base):
    __tablename__ = 'client'
    __table_args__ = {'schema': 'infolica'}
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


class ClientMoralPersonne(Base):
    __tablename__ = 'client_moral_personne'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    client_id = Column(BigInteger, ForeignKey(Client.id), nullable=False)
    titre = Column(Text)
    nom = Column(Text, nullable=False)
    prenom = Column(Text, nullable=False)


class Plan(Base):
    __tablename__ = 'plan'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cadastre_id = Column(BigInteger, ForeignKey(Cadastre.id), nullable=False)
    nom = Column(Text, nullable=False)
    echelle = Column(BigInteger, nullable=False)
    chemin = Column(Text)


class AffaireType(Base):
    __tablename__ = 'affaire_type'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)
    ordre = Column(BigInteger)
    reservation_numeros_types_id = Column(ARRAY(BigInteger))
    modif_affaire_type_id_vers = Column(ARRAY(BigInteger))


class Affaire(Base):
    __tablename__ = 'affaire'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    no_access = Column(Text)
    nom = Column(Text)
    client_commande_id = Column(BigInteger, ForeignKey(Client.id))
    client_commande_complement = Column(Text)
    client_envoi_id = Column(BigInteger, ForeignKey(Client.id))
    client_envoi_complement = Column(Text)
    responsable_id = Column(BigInteger, ForeignKey(Operateur.id))
    technicien_id = Column(BigInteger, ForeignKey(
        Operateur.id), nullable=False)
    type_id = Column(BigInteger, ForeignKey(
        AffaireType.id), nullable=False)
    cadastre_id = Column(BigInteger, ForeignKey(Cadastre.id), nullable=False)
    information = Column(Text)
    date_ouverture = Column(
        Date, default=datetime.datetime.utcnow, nullable=False)
    date_validation = Column(Date)
    date_envoi = Column(Date)
    date_cloture = Column(Date)
    localisation_E = Column(Float, nullable=False)
    localisation_N = Column(Float, nullable=False)
    vref = Column(Text)
    chemin = Column(Text)


class AffaireEtapeIndex(Base):
    __tablename__ = 'affaire_etape_index'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)
    ordre = Column(BigInteger)


class AffaireEtape(Base):
    __tablename__ = 'affaire_etape'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    etape_id = Column(BigInteger, ForeignKey(AffaireEtapeIndex.id), nullable=False)
    date = Column(Date, default=datetime.datetime.utcnow(), nullable=False)
    remarque = Column(Text)


class ModificationAffaireType(Base):
    __tablename__ = 'modification_affaire_type'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)
    ordre = Column(BigInteger)
    reservation_numeros_types_id = Column(ARRAY(BigInteger))
    affaire_source_type_id = Column(ARRAY(BigInteger))


class ModificationAffaire(Base):
    __tablename__ = 'modification_affaire'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id_mere = Column(Integer, ForeignKey(Affaire.id), nullable=False)
    affaire_id_fille = Column(Integer, ForeignKey(Affaire.id), nullable=False)
    type_id = Column(BigInteger, ForeignKey(
        ModificationAffaireType.id), nullable=False)
    date = Column(Date, default=datetime.datetime.utcnow, nullable=False)


class Facture(Base):
    __tablename__ = 'facture'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sap = Column(Text)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    client_id = Column(BigInteger, ForeignKey(Client.id), nullable=False)
    client_co_id = Column(BigInteger, ForeignKey(Client.id))
    client_complement = Column(Text)
    client_premiere_ligne = Column(Text)
    indice_application_mo = Column(Float, default=1.2)
    indice_tva = Column(Float, default=7.7)
    montant_mo = Column(Float, default=0.0, nullable=False)
    montant_rf = Column(Float, default=0.0, nullable=False)
    montant_mat_diff = Column(Float, default=0.0, nullable=False)
    montant_tva = Column(Float, default=0.0, nullable=False)
    montant_total = Column(Float, default=0.0, nullable=False)
    date = Column(Date)
    remarque = Column(Text)


class TableauEmoluments(Base):
    __tablename__ = 'tableau_emoluments'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    domaine = Column(Text, nullable=False)
    categorie = Column(Text, nullable=False)
    sous_categorie = Column(Text, nullable=False)
    nom = Column(Text, nullable=False)
    unite = Column(Text, nullable=False)
    montant = Column(Float, default=0.0, nullable=False)


class EmolumentFacture(Base):
    __tablename__ = 'emolument_facture'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    facture_id = Column(BigInteger, ForeignKey(Facture.id), nullable=False)
    emolument_id = Column(BigInteger, ForeignKey(
        TableauEmoluments.id), nullable=False)
    nombre = Column(Integer, nullable=False)
    facteur_correctif = Column(Float, default=1.0, nullable=False)
    batiment = Column(Text)
    montant = Column(Float, default=0.0, nullable=False)


class RemarqueAffaire(Base):
    __tablename__ = 'remarque_affaire'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    remarque = Column(Text, nullable=False)
    operateur_id = Column(BigInteger, ForeignKey(Operateur.id), nullable=False)
    date = Column(Date, default=datetime.datetime.utcnow, nullable=False)


class DocumentType(Base):
    __tablename__ = 'document_type'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class Document(Base):
    __tablename__ = 'document'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)
    chemin = Column(Text, nullable=False)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    type_id = Column(BigInteger, ForeignKey(DocumentType.id), nullable=False)

class EnvoiType(Base):
    __tablename__ = 'envoi_type'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class Envoi(Base):
    __tablename__ = 'envoi'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    client_id = Column(BigInteger, ForeignKey(Client.id), nullable=False)
    client_complement = Column(Text)
    type_id = Column(BigInteger, ForeignKey(EnvoiType.id))
    date = Column(Date, default=datetime.datetime.utcnow)


class EnvoiDocument(Base):
    __tablename__ = 'envoi_document'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    envoi_id = Column(BigInteger, ForeignKey(Envoi.id), nullable=False)
    document_id = Column(BigInteger, ForeignKey(Document.id), nullable=False)


class SuiviMandatStatut(Base):
    __tablename__ = 'suivi_mandat_statut'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class SuiviMandat(Base):
    __tablename__ = 'suivi_mandat'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id))
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
    pdt_42 = Column(
        Text)  # REMARQUE CONTROLE DE L'ENREGISTREMENT DE TOUS LES DOCUMENTS (COURRIEL, COURRIER, PREAVIS, PLAN, ETC…)
    ap_11 = Column(Boolean)  # RESPECT DES DIRECTIVES DU SCAT, SAGR OU SERVICE URBANISME
    ap_12 = Column(Text)  # REMARQUE RESPECT DES DIRECTIVES DU SCAT, SAGR OU SERVICE URBANISME
    ap_21 = Column(Boolean)  # STRUCTURE DES REPERTOIRES ET CONTENU
    ap_22 = Column(Text)  # REMARQUE STRUCTURE DES REPERTOIRES ET CONTENU
    ap_31 = Column(Boolean)  # GENERATION DE L’ETAT DESCRIPTIF POUR TERRIS
    ap_32 = Column(BigInteger, ForeignKey(Operateur.id))  # CHEF DE PROJET
    ap_33 = Column(Date)  # DATE GENERATION DE L’ETAT DESCRIPTIF POUR TERRIS
    ap_41 = Column(Boolean)  # CONTROLE DE LA BASE DE DONNEES
    ap_42 = Column(Text)  # REMARQUE CONTROLE DE LA BASE DE DONNEES
    visa = Column(BigInteger, ForeignKey(Operateur.id))
    date = Column(Date)


class ControleMutation(Base):
    __tablename__ = 'controle_mutation'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id))
    bf_1 = Column(
        Boolean)  # Contrôler les numéros des points limites ainsi que la valeur, la prévision et la fiabilité des points sont en adéquation avec le niveau de tolérence de la zone de travail
    bf_2 = Column(
        Boolean)  # Contrôler dans la table « Bien_fonds => Mise_a_jourBF » qu’il y que les nouveaux biens-fonds créés dans votre affaire et qu'il n'y a pas de biens-fonds sans géométrie
    bf_3 = Column(
        Boolean)  # Contrôler dans la table « Bien_fonds » que l’attribut « Validation_juridique » est non pour les nouveaux biens-fonds sauf pour les nouveaux DP.
    bf_4 = Column(
        Boolean)  # Contrôler dans la table « Biens_fonds.PosImmeuble » que les éléments suivants sont corrects (Hali=Center, Vali=Half, Grandeur=Petite.petite).
    cs_1 = Column(
        Boolean)  # Contrôler les numéros des points particuliers "660" ainsi que la valeur, la précision et la fiabilité des points sont en adéquations avec le niveau de tolérance de la zone de travail.
    cs_2 = Column(
        Boolean)  # Contrôler dans la table « Couverture_du_sol => Mise_a_jourCS » qu’il y a que les nouvelles surfaces créées dans votre affaire qu'il n'y a pas de surfaces sans géométrie.
    cs_3 = Column(
        Boolean)  # Contrôler dans la table « Couverture_du_sol => PosNumero_de_batiment » que les éléments suivants sont corrects (Hali=Center, Vali=Base, Grandeur=Petite.tres_petite).
    cs_4 = Column(Boolean)  # Insérer les points dans la base Acces des bâtiments projets (voir Processus)
    cs_5 = Column(Boolean)  # Contrôler la géométrie des EGID (01.01.2012).
    od_1 = Column(Boolean)  # Tous les points de constructions "760" sont supprimés.
    od_2 = Column(
        Boolean)  # Contrôler les nouveaux éléments créés dans votre affaire et qu'il n'y a pas d'objets divers sans géométrie.
    od_3 = Column(Boolean)  # Contrôler que les bâtiments souterrains ont les bons numéros et une désignation.
    od_4 = Column(Boolean)  # Insérer les points dans la base Acces des bâtiments projets (voir Processus)
    od_5 = Column(
        Boolean)  # Contrôler que l'attribut « Objets_divers => SymboleElement_surfacique » est rempli pour les piscines.
    bat_1 = Column(
        Boolean)  # Contrôler dans la table « Adresses_des_batiments => Mise_a_jourBAT » qu’il y a bien que les nouveaux éléments que vous avez créés dans votre affaire.
    bat_2 = Column(
        Boolean)  # Contrôler dans la table « Adresses_des_batiments => PosNumero_maison » que les éléments suivants sont corrects (Hali=Center, Vali=Half, Grandeur=Petite.assez_petite).
    bat_3 = Column(Boolean)  # Contrôler que les points adresses sont dans les géométries.
    serv_1 = Column(
        Boolean)  # Contrôler dans la table « Servitudes => Mise_a_jourSE » qu’il y a bien que les nouveaux éléments que vous avez créés dans votre affaire.
    serv_2 = Column(
        Boolean)  # Contrôler dans la table « Servitudes => Servitude_surface » ou « Servitudes => Servitude_ligne » ou « Servitudes => Servitude_point » que l’attribut « Validite » est en_projet pour les nouvelles servitudes.
    serv_3 = Column(
        Boolean)  # Contrôler dans la table « Servitudes => PosNumero_de_servitude » que les éléments suivants sont corrects (Hali=Left, Vali=Base, Grandeur= -).
    nom_1 = Column(Boolean)  # A partir de deux noms locaux pour un bien-fonds vérifier si cela est exact.
    suiv_mut_1 = Column(Boolean)  # Supprimer dans la gestion des mutations les « Topic » qui ne sont pas utilisés.
    suiv_mut_2 = Column(Boolean)  # Mutation "En cours/Libérée".
    div_1 = Column(Boolean)  # Épurations des fichiers dans le répertoire de l’affaire.
    div_2 = Column(
        Boolean)  # Contrôler que vous avez bien saisi le dernier numéro de point de l’affaire concernée dans le programme « Réservation des numéros ».
    div_3 = Column(
        Boolean)  # Contrôler rigoureusement les désignations, la balance ainsi que les observations pour le registre foncier.
    visa = Column(BigInteger, ForeignKey(Operateur.id))
    date = Column(Date)


class ControlePPE(Base):
    __tablename__ = 'controle_ppe'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    doss_proj_1 = Column(Boolean)  # Faisabilité de la PPE (projet de division, Bien-fonds en vigueur?)
    doss_proj_2 = Column(Boolean)  # Aucune PPE ne doit être déjà constituée sur le bien-fonds concerné
    psit_1 = Column(Boolean)  # Contrôler la référence de la source des données cadastrales et de sa date d’émission
    psit_2 = Column(Boolean)  # Nord, échelle 1:500
    psit_3 = Column(Boolean)  # Contenu du plan (bâtiment projet) et graphisme de la couche bien-fonds
    psit_4 = Column(Boolean)  # Contrôle de l'échelle (kutch)
    psit_5 = Column(
        Boolean)  # Cartouche (Cadastre de … PPE sur le bien-fonds …. – Plan de situation - XXX, architecte, signature, date)
    psit_6 = Column(
        Boolean)  # Droits de jouissance clairement définis (liseré traitillé même couleur que l'unité concernée) "Droit de jouissance au profit de l'unité …"
    psit_7 = Column(
        Boolean)  # Places de parcs extérieures numérotées (uniquement si les places ne sont pas constituées en droit de jouissance)
    pamext_1 = Column(
        Boolean)  # Ce plan n'est pas un document obligatoire, mais si l'architecte décide de le joindre avec le dossier le contrôle sera identique au plan de situation (Échelle ≠ 1:500)
    pet_1 = Column(Boolean)  # Nord (pas obligatoire), Échelle 1:100
    pet_2 = Column(Boolean)  # Contrôle de l'échelle (kutch)
    pet_3 = Column(Boolean)  # Cartouche (Cadastre de … PPE sur le bien-fonds …, architecte, signature, date)
    pet_4 = Column(Boolean)  # Cotes générales
    pet_5 = Column(
        Boolean)  # Informations superflues à supprimer (surfaces des pièces, matériaux, limites de bien-fonds etc.)
    pet_6 = Column(Boolean)  # Appellations des locaux
    pet_7 = Column(
        Boolean)  # Faisabilité d'unité d'étage: Un tout indépendant; Local physiquement fermé (surface minimum); Certain degré d'autonomie économique; Accès propre
    pet_8 = Column(
        Boolean)  # Distribution lettres unités (de bas en haut / A, B, … Z, AA, AB etc.). Le "i" n'est pas utilisé!
    pet_9 = Column(
        Boolean)  # Les annexes ont les mêmes lettres et mêmes couleurs de liserés que les unités concernées. Chiffres arabe (EX A1, B3, D1 etc.)
    pet_10 = Column(
        Boolean)  # Périmètres (liserés) des unités d'étages clairement dessinés (zone tampon / éviter la couleur jaune)
    pet_11 = Column(
        Boolean)  # Murs porteurs, piliers, poutres, gaines techniques etc ne font pas parties des parties exclusives -> parties communes -> liserés de couleur
    pet_12 = Column(
        Boolean)  # Conditions pièce -> appellation "chambre": Surface minimum: 10m2; Surface éclairage ≥ 1/8ème surface plancher; Local physiquement fermé
    pet_13 = Column(Boolean)  # La pièce ne peut pas être considérée comme chambre -> "disponible"
    pet_14 = Column(Boolean)  # Y a-t-il une surface plancher sous l'escalier ou un réduit (local fermé)
    pet_15 = Column(
        Boolean)  # Les vides (escaliers, vide sur chambres, etc.) doivent être hachurés avec la même couleur que l'unité concernée
    pet_16 = Column(
        Boolean)  # Accès aux parties communes par des parties privées (rares exceptions -> servitude de passage)
    pet_17 = Column(
        Boolean)  # Les balcons font partie de l'unité ou sont des droits de jouissance (parties construites)
    pet_18 = Column(Boolean)  # Autres bâtiments sur le bien-fonds concerné -> plans d'étages, façades, coupes
    pet_19 = Column(Boolean)  # Concordance des appellations sur les plans d'étages avec les formules de légende
    pet_20 = Column(Boolean)  # Lignes de coupes sur tous les plans d'étages
    pet_21 = Column(Boolean)  # Surfaces PDF Viewer (tolérance jusqu'à 2 %)
    pco_1 = Column(Boolean)  # Échelle 1:100
    pco_2 = Column(Boolean)  # Sans liseré ni lettre d'unité
    pco_3 = Column(Boolean)  # Contrôle de l'échelle (kutch)
    pco_4 = Column(Boolean)  # Cartouche (Cadastre de … PPE sur le bien-fonds …., architecte, signature, date)
    pco_5 = Column(
        Boolean)  # Les appellations, si notées sur les plans de coupe, doivent correspondre avec les appellations des plans d'étages
    pco_6 = Column(Boolean)  # Concordance de la / les coupe(s) avec les plans d'étages (par plaquage)
    pco_7 = Column(Boolean)  # Informations superflues à supprimer (surfaces des pièces, matériaux, etc.)
    facade_1 = Column(Boolean)  # Échelle 1:100
    facade_2 = Column(Boolean)  # Cartouche (Cadastre de … PPE sur le bien-fonds …., architecte, signature, date)
    facade_3 = Column(Boolean)  # Sans liseré ni lettre d'unité
    facade_4 = Column(
        Boolean)  # Concordance avec tous les plans d'étages (ouvertures, portes, fenêtres, velux, cheminées) -> plaquage
    form_leg_1 = Column(Boolean)  # Titres (Cadastre de …– Plan de situation – XXX - PPE sur le bien-fonds ….)
    form_leg_2 = Column(
        Boolean)  # Situation de l'unité juridique dans l'espace (appartement ouest, extrême ouest, N° entrée etc.)
    form_leg_3 = Column(
        Boolean)  # Étages clairement définis (1er étage, niveau -1, etc.) concordance avec les plans d'étages
    form_leg_4 = Column(
        Boolean)  # Concordance entre les appellations des pièces sur les plans d'étages avec la formule de légende
    form_leg_5 = Column(Boolean)  # Les éléments de liaison doivent être notés (escalier, escalier escamotable)
    form_leg_6 = Column(Boolean)  # Appellations avec quantité (1 cuisine, 3 chambres etc.)
    form_leg_7 = Column(Boolean)  # Mise en page (unités en duplex, Annexes etc.)
    form_leg_8 = Column(Boolean)  # Concordance surfaces architecte avec surfaces obtenues par PDF Viewer (tol 2%)
    form_leg_9 = Column(Boolean)  # Récapitulatif
    fact_1 = Column(Boolean)  # 1 mandat
    fact_2 = Column(Boolean)  # X unités simples ou complexes (unités juridiques, annexes)
    fact_3 = Column(
        Boolean)  # Droits de jouissance X surfaces (seulement si les surfaces sont notées sur les plans d'étage)
    fact_4 = Column(Boolean)  # Régie (séances, renseignements, contrôle dossier supplémentaire etc)
    fact_5 = Column(Boolean)  # Données numériques fournies ou plan de situation
    fact_6 = Column(Boolean)  # Report des montants de la facture sur le formulaire de demande
    fact_7 = Column(Boolean)  # Impression facture -> datée et signée
    visa = Column(BigInteger, ForeignKey(Operateur.id))
    date = Column(Date)


class NumeroType(Base):
    __tablename__ = 'numero_type'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)
    ordre = Column(BigInteger)
    
    
class NumeroEtat(Base):
    __tablename__ = 'numero_etat'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class Numero(Base):
    __tablename__ = 'numero'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cadastre_id = Column(BigInteger, ForeignKey(Cadastre.id), nullable=False)
    type_id = Column(BigInteger, ForeignKey(NumeroType.id), nullable=False)
    numero = Column(BigInteger, nullable=False)
    suffixe = Column(Text)
    etat_id = Column(BigInteger, ForeignKey(NumeroEtat.id), nullable=False)
    plan_id = Column(BigInteger, ForeignKey(Plan.id))

    UniqueConstraint(cadastre_id, type_id, plan_id, numero)


class NumeroEtatHisto(Base):
    __tablename__ = 'numero_etat_histo'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    numero_id = Column(BigInteger, ForeignKey(Numero.id), nullable=False)
    numero_etat_id = Column(BigInteger, ForeignKey(
        NumeroEtat.id), nullable=False)
    date = Column(Date, default=datetime.datetime.utcnow, nullable=False)


class NumeroDiffere(Base):
    __tablename__ = 'numero_differe'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    numero_id = Column(BigInteger, ForeignKey(Numero.id), nullable=False)
    date_entree = Column(
        Date, default=datetime.datetime.utcnow, nullable=False)
    date_sortie = Column(Date)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id))


class NumeroRelationType(Base):
    __tablename__ = 'numero_relation_type'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class NumeroRelation(Base):
    __tablename__ = 'numero_relation'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    numero_id_base = Column(Integer, ForeignKey(Numero.id), nullable=False)
    numero_id_associe = Column(Integer, ForeignKey(Numero.id), nullable=False)
    relation_type_id = Column(BigInteger, ForeignKey(
        NumeroRelationType.id), nullable=False)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id))


# class NumeroPlan(Base):
#     __tablename__ = 'numero_plan'
#     __table_args__ = {'schema': 'infolica'}
#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     numero_id = Column(BigInteger, ForeignKey(Numero.id), nullable=False)
#     plan_id = Column(BigInteger, ForeignKey(Plan.id), nullable=False)


class AffaireNumeroType(Base):
    __tablename__ = 'affaire_numero_type'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class AffaireNumero(Base):
    __tablename__ = 'affaire_numero'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    numero_id = Column(BigInteger, ForeignKey(Numero.id), nullable=False)
    type_id = Column(BigInteger, ForeignKey(AffaireNumeroType.id))  # , nullable=False)
    actif = Column(Boolean, default=True, nullable=False)
    affaire_destination_id = Column(BigInteger, ForeignKey(Affaire.id))


class Service(Base):
    __tablename__ = 'service'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    service = Column(Text, nullable=False)
    abreviation = Column(Text, nullable=False)
    nom = Column(Text)
    prenom = Column(Text)
    adresse = Column(Text)
    npa = Column(Text)
    localite = Column(Text)
    telephone = Column(Text)
    mail = Column(Text)


class PreavisType(Base):
    __tablename__ = 'preavis_type'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class Preavis(Base):
    __tablename__ = 'preavis'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    affaire_id = Column(BigInteger, ForeignKey(Affaire.id), nullable=False)
    service_id = Column(BigInteger, ForeignKey(Service.id), nullable=False)
    preavis_type_id = Column(BigInteger, ForeignKey(PreavisType.id))
    date_demande = Column(
        Date, default=datetime.datetime.utcnow, nullable=False)
    date_reponse = Column(Date)
    remarque = Column(Text)


# class RemarquePreavis(Base):  # currently not used, replaced by attribute Remarque in table Preavis
#     __tablename__ = 'remarque_preavis'
#     __table_args__ = {'schema': 'infolica'}
#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     preavis_id = Column(BigInteger, ForeignKey(Preavis.id), nullable=False)
#     remarque = Column(Text, nullable=False)
#     date = Column(Date, default=datetime.datetime.utcnow, nullable=False)


class Fonction(Base):
    __tablename__ = 'fonction'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class Role(Base):
    __tablename__ = 'role'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nom = Column(Text, nullable=False)


class FonctionRole(Base):
    __tablename__ = 'fonction_role'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    fonction_id = Column(BigInteger, ForeignKey(Fonction.id), nullable=False)
    role_id = Column(BigInteger, ForeignKey(Role.id), nullable=False)

# ======================== VUES ========================


class VNumeros(Base):
    __tablename__ = 'v_numeros'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True)
    cadastre = Column(Text)
    cadastre_id = Column(BigInteger)
    numero = Column(BigInteger)
    suffixe = Column(Text)
    etat = Column(Text)
    etat_id = Column(BigInteger)
    type_numero = Column(Text)
    type_numero_id = Column(BigInteger)
    diff_id = Column(Date)
    diff_entree = Column(Date)
    diff_sortie = Column(Date)
    diff_affaire_id = Column(BigInteger)
    plan_id = Column(BigInteger)


class VNumerosAffaires(Base):
    __tablename__ = 'v_numeros_affaires'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True)
    numero_id = Column(BigInteger)
    affaire_id = Column(BigInteger)
    affaire_numero_type_id = Column(BigInteger)
    affaire_numero_actif = Column(Boolean)
    affaire_destination_id = Column(BigInteger)
    affaire_nom = Column(Text)
    affaire_type = Column(Text)
    affaire_date = Column(Date)
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
    numero_plan_id = Column(BigInteger)
    numero_base_id = Column(BigInteger)
    numero_base_type = Column(Text)
    numero_base = Column(BigInteger)
    numero_base_suffixe = Column(Text)
    numero_base_etat = Column(Text)
    affaire_numero_type = Column(Text)


class VAffaire(Base):
    __tablename__ = 'v_affaires'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True)
    no_access = Column(Text)
    nom = Column(Text)
    client_commande_id = Column(BigInteger)
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
    responsable_id = Column(BigInteger)
    responsable_nom = Column(Text)
    responsable_prenom = Column(Text)
    technicien_id = Column(BigInteger)
    technicien_nom = Column(Text)
    technicien_prenom = Column(Text)
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


class VEnvois(Base):
    __tablename__ = 'v_envois'
    __table_args__ = {'schema': 'infolica'}
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
    __tablename__ = 'v_etapes_affaires'
    __table_args__ = {'schema': 'infolica'}
    affaire_id = Column(BigInteger, primary_key=True)
    affaire_nom = Column(Text)
    etape = Column(Text, primary_key=True)
    date_etape = Column(Date, primary_key=True)
    affaire_liee_id = Column(BigInteger)
    affaire_liee_nom = Column(Text)
    service_nom = Column(Text, primary_key=True)
    remarque = Column(Text)


class VAffairesPreavis(Base):
    __tablename__ = 'v_affaires_preavis'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True)
    affaire_id = Column(BigInteger)
    service = Column(Text)
    service_id = Column(BigInteger)
    preavis = Column(Text)
    preavis_type_id = Column(BigInteger)
    date_demande = Column(Date)
    date_reponse = Column(Date)
    remarque = Column(Text)
    

class VTableauBord(Base):
    __tablename__ = 'v_tableau_de_bord'
    __table_args__ = {'schema': 'infolica'}
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
    __tablename__ = 'v_emoluments_factures'
    __table_args__ = {'schema': 'infolica'}
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
    __tablename__ = 'v_numeros_relations'
    __table_args__ = {'schema': 'infolica'}
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
    numero_base_plan_id = Column(BigInteger)
    numero_associe_id = Column(BigInteger)
    numero_associe_cadastre_id = Column(BigInteger)
    numero_associe_cadastre = Column(Text)
    numero_associe_type_id = Column(BigInteger)
    numero_associe_type = Column(Text)
    numero_associe = Column(BigInteger)
    numero_associe_suffixe = Column(Text)
    numero_associe_etat_id = Column(BigInteger)
    numero_associe_etat = Column(Text)
    numero_associe_plan_id = Column(BigInteger)
    numero_relation_type_id = Column(BigInteger)
    numero_relation_type = Column(Text)


class VDocumentsAffaires(Base):
    __tablename__ = 'v_documents_affaires'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True)
    nom = Column(Text)
    chemin = Column(Text)
    affaire_id = Column(BigInteger)
    type_id = Column(BigInteger)
    type_doc = Column(Text)


class VFactures(Base):
    __tablename__ = 'v_factures'
    __table_args__ = {'schema': 'infolica'}
    id = Column(BigInteger, primary_key=True)
    affaire_id = Column(BigInteger)
    affaire_vref = Column(Text)
    sap = Column(Text)
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
    client_co_id = Column(BigInteger)
    client_co_entreprise = Column(Text)
    client_co_titre = Column(Text)
    client_co_nom = Column(Text)
    client_co_prenom = Column(Text)
    client_co_co = Column(Text)
    client_co_adresse = Column(Text)
    client_co_npa = Column(Text)
    client_co_localite = Column(Text)
    client_co_case_postale = Column(Text)
    client_co_tel_fixe = Column(Text)
    client_co_fax = Column(Text)
    client_co_tel_portable = Column(Text)
    client_co_mail = Column(Text)
    client_co_entree = Column(Date)
    client_co_sortie = Column(Date)
    client_co_no_sap = Column(Text)
    client_co_no_bdp_bdee = Column(Text)
    indice_application_mo = Column(Float)
    indice_tva = Column(Float)
    montant_mo = Column(Float)
    montant_mat_diff = Column(Float)
    montant_rf = Column(Float)
    montant_tva = Column(Float)
    montant_total = Column(Float)
    date = Column(Date)
    remarque = Column(Text)
