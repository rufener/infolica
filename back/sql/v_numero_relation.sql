create view infolica.v_numeros_relations
as
    SELECT numb.id AS numero_base_id,
        cadb.nom AS numero_base_cadastre,
        cadb.id AS numero_base_cadastre_id,
        numtb.nom AS numero_base_type,
        numtb.id AS numero_base_type_id,
        numb.numero AS numero_base_numero,
        numb.suffixe AS numero_base_suffixe,
        numeb.nom AS numero_base_etat,
        numeb.id AS numero_base_etat_id,
        numb.plan_id AS numero_base_plan_id,
        numa.id AS numero_associe_id,
        cada.nom AS numero_associe_cadastre,
        cada.id AS numero_associe_cadastre_id,
        numta.nom AS numero_associe_type,
        numta.id AS numero_associe_type_id,
        numa.numero AS numero_associe_numero,
        numa.suffixe AS numero_associe_suffixe,
        numea.nom AS numero_associe_etat,
        numea.id AS numero_associe_etat_id,
        numa.plan_id AS numero_associe_plan_id,
        numrt.nom AS relation_type,
        numrt.id AS relation_type_id,
        numr.affaire_id
    FROM infolica.numero numb,
        infolica.numero numa,
        infolica.numero_relation numr,
        infolica.numero_relation_type numrt,
        infolica.cadastre cadb,
        infolica.cadastre cada,
        infolica.numero_type numta,
        infolica.numero_type numtb,
        infolica.numero_etat numeb,
        infolica.numero_etat numea
    WHERE numr.numero_id_base = numb.id 
        AND numr.numero_id_associe = numa.id 
        AND numr.relation_type_id = numrt.id 
        AND numb.cadastre_id = cadb.id 
        AND numa.cadastre_id = cada.id 
        AND numb.type_id = numtb.id 
        AND numa.type_id = numta.id 
        AND numb.etat_id = numeb.id 
        AND numa.etat_id = numea.id
    ORDER BY numr.affaire_id;
