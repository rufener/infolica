create view infolica.v_affaires as
 SELECT aff.id,
    aff.nom,
    cl.id AS client_commande_id,
    cl.entreprise AS client_commande_entreprise,
    cl.titre AS client_commande_titre,
    cl.nom AS client_commande_nom,
    cl.prenom AS client_commande_prenom,
    clp.id AS client_commande_par_id,
    clp.entreprise AS client_commande_par_entreprise,
    clp.titre AS client_commande_par_titre,
    clp.nom AS client_commande_par_nom,
    clp.prenom AS client_commande_par_prenom,
    op.id AS responsable_id,
    op.nom AS responsable_nom,
    op.prenom AS responsable_prenom,
    op2.id AS technicien_id,
    op2.nom AS technicien_nom,
    op2.prenom AS technicien_prenom,
    afft.nom AS type_affaire,
    cad.nom AS cadastre,
    aff.information,
    aff.date_ouverture,
    aff.date_validation,
    aff.date_cloture,
    aff."localisation_E" AS localisation_e,
    aff."localisation_N" AS localisation_n,
    aff.cadastre_id,
    aff.type_id,
    aff.vref,
    aff.chemin
   FROM infolica.affaire aff
     LEFT JOIN infolica.client cl ON aff.client_commande_id = cl.id
     LEFT JOIN infolica.client clp ON aff.client_commande_par_id = clp.id
     LEFT JOIN infolica.operateur op ON aff.responsable_id = op.id
     LEFT JOIN infolica.operateur op2 ON aff.technicien_id = op2.id
     LEFT JOIN infolica.affaire_type afft ON aff.type_id = afft.id
     LEFT JOIN infolica.cadastre cad ON aff.cadastre_id = cad.id;