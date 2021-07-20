def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    #Test api
    config.add_route('api_test', '/infolica/api/test')
    #Clients
    config.add_route('types_clients', '/infolica/api/types_clients')
    config.add_route('types_clients_s', '/infolica/api/types_clients/')
    config.add_route('clients', '/infolica/api/clients')
    config.add_route('clients_s', '/infolica/api/clients/')
    config.add_route('client_by_id', '/infolica/api/clients/{id}')
    config.add_route('recherche_clients', '/infolica/api/recherche_clients')
    config.add_route('recherche_clients_s', '/infolica/api/recherche_clients/')
    config.add_route('client_moral_personnes_by_client_id', '/infolica/api/client_moral_personnes/{client_id}')
    config.add_route('client_moral_personnes', '/infolica/api/client_moral_personnes')
    config.add_route('client_moral_personnes_s', '/infolica/api/client_moral_personnes/')
    #Affaires
    config.add_route('affaires', '/infolica/api/affaires')
    config.add_route('affaires_s', '/infolica/api/affaires/')
    config.add_route('affaire_spatial', '/infolica/api/affaires/spatial')
    config.add_route('types_affaires', '/infolica/api/types_affaires')
    config.add_route('types_affaires_s', '/infolica/api/types_affaires/')
    config.add_route('affaire_by_id', '/infolica/api/affaires/{id}')
    config.add_route('recherche_affaires', '/infolica/api/recherche_affaires')
    config.add_route('recherche_affaires_s', '/infolica/api/recherche_affaires/')
    config.add_route('types_modification_affaire', '/infolica/api/types_modification_affaire')
    config.add_route('types_modification_affaire_s', '/infolica/api/types_modification_affaire/')
    config.add_route('modification_affaires', '/infolica/api/modification_affaires')
    config.add_route('modification_affaires_s', '/infolica/api/modification_affaires/')
    config.add_route('modification_affaire_by_affaire_mere', '/infolica/api/modification_affaire_by_affaire_mere/{id}')
    config.add_route('modification_affaire_by_affaire_fille', '/infolica/api/modification_affaire_by_affaire_fille/{id}')
    config.add_route('affaires_cockpit', '/infolica/api/affaires_cockpit')
    config.add_route('abandon_affaire_reopen_parent_affaire', '/infolica/api/abandon_affaire_reopen_parent_affaire')
    #Factures
    config.add_route('factures', '/infolica/api/factures')
    config.add_route('factures_s', '/infolica/api/factures/')
    config.add_route('facture_by_id', '/infolica/api/factures/{id}')
    config.add_route('affaires_factures_by_affaire_id', '/infolica/api/affaires_factures/{id}')
    #Login
    config.add_route('login', '/infolica/api/login')
    config.add_route('login_s', '/infolica/api/login/')
    config.add_route('logout', '/infolica/api/logout')
    #Operateur
    config.add_route('operateurs', '/infolica/api/operateurs')
    config.add_route('operateurs_s', '/infolica/api/operateurs/')
    config.add_route('operateur_by_id', '/infolica/api/operateurs/{id}')
    config.add_route('recherche_operateurs', '/infolica/api/recherche_operateurs')
    config.add_route('recherche_operateurs_s', '/infolica/api/recherche_operateurs/')
    config.add_route('add_operateurs_ad', '/infolica/api/add_operateurs_ad')
    config.add_route('add_operateurs_ad_s', '/infolica/api/add_operateurs_ad/')
    #Test (temp endpoint)
    config.add_route('test_client', '/infolica/api/test_client')
    #Controle_mutation
    config.add_route('controles_mutations','/infolica/api/controles_mutations')
    config.add_route('controles_mutations_s','/infolica/api/controles_mutations/')
    config.add_route('controle_mutation_by_id', '/infolica/api/controles_mutations/{id}')
    config.add_route('controle_mutation_by_affaire_id', '/infolica/api/affaire_controles_mutations/{id}')
    #Controle_PPE
    config.add_route('controles_ppe','/infolica/api/controles_ppe')
    config.add_route('controles_ppe_s','/infolica/api/controles_ppe/')
    config.add_route('controle_ppe_by_id', '/infolica/api/controles_ppe/{id}')
    config.add_route('controle_ppe_by_affaire_id', '/infolica/api/affaire_controles_ppe/{id}')
    #Controle_geometre
    config.add_route('controle_geometre','/infolica/api/controle_geometre')
    config.add_route('controle_geometre_s','/infolica/api/controle_geometre/')
    config.add_route('controle_geometre_by_affaire_id', '/infolica/api/affaire_controle_geometre/{id}')
    #Numéros
    config.add_route('numeros','/infolica/api/numeros')
    config.add_route('numeros_s','/infolica/api/numeros/')
    config.add_route('types_numeros','/infolica/api/types_numeros')
    config.add_route('types_numeros_s','/infolica/api/types_numeros/')
    config.add_route('etats_numeros','/infolica/api/etats_numeros')
    config.add_route('etats_numeros_s','/infolica/api/etats_numeros/')
    config.add_route('recherche_numeros','/infolica/api/recherche_numeros')
    config.add_route('recherche_numeros_s','/infolica/api/recherche_numeros/')
    config.add_route('numero_by_id', '/infolica/api/numeros/{id}')
    config.add_route('numero_base_relations_by_id', '/infolica/api/numero_base_relations/{id}')
    config.add_route('numero_associe_relations_by_id', '/infolica/api/numero_associe_relations/{id}')
    config.add_route('numeros_relations','/infolica/api/numeros_relations')
    config.add_route('numeros_relations_s','/infolica/api/numeros_relations/')
    config.add_route('numeros_relation_by_affaire_id','/infolica/api/affaire_numeros_relations/{id}')
    # config.add_route('numeros_relations_by_numeroBase','/infolica/api/numeros_relations_by_numeroBase_id')
    # config.add_route('numeros_relations_by_numeroBase_s','/infolica/api/numeros_relations_by_numeroBase_id/')
    config.add_route('numeros_differes','/infolica/api/numeros_differes')
    config.add_route('numeros_differes_s','/infolica/api/numeros_differes/')
    #Référence de numéros
    config.add_route('reference_numeros','/infolica/api/reference_numeros')
    config.add_route('reference_numeros_s','/infolica/api/reference_numeros/')
    #Réservation de numéros
    config.add_route('reservation_numeros','/infolica/api/reservation_numeros')
    config.add_route('reservation_numeros_s','/infolica/api/reservation_numeros/')
    #AffairesNuméros
    config.add_route('affaire_numeros','/infolica/api/affaire_numeros')
    config.add_route('affaire_numeros_s','/infolica/api/affaire_numeros/')
    config.add_route('affaire_numeros_by_affaire_id','/infolica/api/affaire_numeros/{id}')
    config.add_route('affaire_numeros_MO_by_affaire_id', '/infolica/api/numeros_mo_affaire/{id}')
    config.add_route('desactiver_numeros_affaires','/infolica/api/desactiver_numeros_affaires')
    config.add_route('desactiver_numeros_affaires_s','/infolica/api/desactiver_numeros_affaires/')
    #Historique numéros
    config.add_route('numeros_etat_histo','/infolica/api/numeros_etat_histo')
    config.add_route('numeros_etat_histo_s','/infolica/api/numeros_etat_histo/')
    #Etapes affaire
    config.add_route('etapes_by_id','/infolica/api/etapes/{id}')
    config.add_route('etapes','/infolica/api/etapes')
    config.add_route('etapes_s','/infolica/api/etapes/')
    config.add_route('etapes_index','/infolica/api/etapes_index')
    config.add_route('etapes_index_s','/infolica/api/etapes_index/')
    config.add_route('affaire_etapes_by_affaire_id','/infolica/api/affaire_etapes/{id}')
    #Numeros affaires
    config.add_route('numero_affaires_by_numero_id','/infolica/api/numero_affaires/{id}')
    #Preavis affaire
    config.add_route('preavis','/infolica/api/preavis')
    config.add_route('preavis_s','/infolica/api/preavis/')
    config.add_route('preavis_type','/infolica/api/preavis_type')
    config.add_route('preavis_type_s','/infolica/api/preavis_type/')
    config.add_route('affaire_preavis_by_affaire_id','/infolica/api/affaire_preavis/{id}')
    #Documents affaire
    config.add_route('affaire_dossier_by_affaire_id', '/infolica/api/affaire_dossier/{id}')
    config.add_route('affaire_documents_by_affaire_id','/infolica/api/affaire_documents/{id}')
    config.add_route('types_documents', '/infolica/api/types_documents')
    config.add_route('types_documents_s', '/infolica/api/types_documents/')
    config.add_route('upload_affaire_document', '/infolica/api/upload_affaire_document')
    config.add_route('download_affaire_document', '/infolica/api/download_affaire_document')
    config.add_route('download_affaire_document_s', '/infolica/api/download_affaire_document/')
    config.add_route('courrier_affaire', '/infolica/api/courrier_affaire')
    config.add_route('courrier_affaire_s', '/infolica/api/courrier_affaire/')
    config.add_route('delete_affaire_document', '/infolica/api/delete_affaire_document')
    config.add_route('save_document', '/infolica/api/save_document')
    #Emoluments facture
    config.add_route('emolument_facture_by_id','/infolica/api/emolument_facture/{id}')
    config.add_route('emolument_facture','/infolica/api/emolument_facture')
    config.add_route('emolument_facture_s','/infolica/api/emolument_facture/')
    config.add_route('facture_emoluments_by_facture_id','/infolica/api/facture_emoluments/{id}')
    #Envois
    config.add_route('envois_by_id','/infolica/api/envois/{id}')
    config.add_route('envois','/infolica/api/envois')
    config.add_route('envois_s','/infolica/api/envois/')
    config.add_route('envois_types','/infolica/api/envois_type')
    config.add_route('envois_types_s','/infolica/api/envois_type/')
    config.add_route('affaire_envois_by_affaire_id','/infolica/api/affaire_envois/{id}')
    #Suivi Mandat
    config.add_route('suivi_mandat_by_id','/infolica/api/suivi_mandats/{id}')
    config.add_route('suivi_mandats','/infolica/api/suivi_mandats')
    config.add_route('suivi_mandats_s','/infolica/api/suivi_mandats/')
    config.add_route('affaire_suivi_mandats_by_affaire_id','/infolica/api/affaire_suivi_mandats/{id}')
    #Cadastres
    config.add_route('cadastres','/infolica/api/cadastres')
    config.add_route('cadastres_s','/infolica/api/cadastres/')
    # Fonctions & roles
    config.add_route('fonctions', '/infolica/api/fonctions')
    config.add_route('fonctions_s', '/infolica/api/fonctions/')
    config.add_route('roles', '/infolica/api/roles')
    config.add_route('roles_s', '/infolica/api/roles/')
    config.add_route('fonctions_roles_by_id', '/infolica/api/fonctions_roles/{id}')
    config.add_route('fonctions_roles_current_user', '/infolica/api/fonctions_roles_current_user')
    #Services
    config.add_route('service_by_id','/infolica/api/services/{id}')
    config.add_route('services','/infolica/api/services')
    config.add_route('services_s','/infolica/api/services/')
    #Balance
    config.add_route('balance_generate_table', '/infolica/api/balance_generate')
    config.add_route('balance_mutation_names', '/infolica/api/balance_mutation_names')
    config.add_route('balance_by_affaire_id', '/infolica/api/balance')
    config.add_route('balance_check_existing_oldBF', '/infolica/api/balance_check_existing_oldbf')
    config.add_route('balance_files_by_affaire_id', '/infolica/api/balance_files')
    config.add_route('balance_from_file', '/infolica/api/balance_from_file')
    #Reservation_numeros_mo
    config.add_route('reservation_numeros_mo_by_affaire_id', '/infolica/api/reservation_numeros_mo/{id}')
    config.add_route('reservation_numeros_mo', '/infolica/api/reservation_numeros_mo')
    #Plans MO
    config.add_route('plans_mo', '/infolica/api/plans_mo')
    #Numéro MO next available
    config.add_route('numero_mo_next', '/infolica/api/numero_mo_next')
    config.add_route('types_numeros_mo', '/infolica/api/types_numeros_mo')
    #Open Folder
    config.add_route('open_folder', '/infolica/api/open_folder')
    #Notes de mise à jour
    config.add_route('notes_maj', '/infolica/api/notes_maj')


