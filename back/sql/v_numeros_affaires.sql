create view infolica.v_numeros_affaires as
select affnum.numero_id as numero_id, aff.id as affaire_id, affnum.type_id as affaire_numero_type_id, aff.nom as affaire_nom, afft.nom as affaire_type, 
aff.date_ouverture as affaire_date, aff.information as affaire_information, cad.nom as numero_cadastre, cad.id as numero_cadastre_id, numt.nom as numero_type,
num.type_id as numero_type_id, num.numero as numero, 
num.suffixe as numero_suffixe, nume.nom as numero_etat, nume.id as numero_etat_id, affnumt.nom as affaire_numero_type, numdiff.id as numero_diff_id, 
numdiff.date_entree as numero_diff_entree, numdiff.date_sortie as numero_diff_sortie, num.plan_id as numero_plan_id, tmp.numero_base_id as numero_base_id,
tmp.numero_base_type as numero_base_type, tmp.numero_base as numero_base, tmp.numero_base_suffixe as numero_base_suffixe, tmp.numero_base_etat as numero_base_etat
from infolica.affaire_numero as affnum 
left join (select numr.affaire_id as affaire_id, numr.numero_id_associe as numero_associe_id, numb.numero as numero_base, numeb.nom as numero_base_etat, 
		    numtb.nom as numero_base_type, numr.numero_id_base as numero_base_id, numb.suffixe as numero_base_suffixe
			from infolica.numero_relation numr, infolica.numero as numb, infolica.numero_type as numtb, infolica.numero_etat as numeb
			where numr.numero_id_base = numb.id
			and numb.type_id = numtb.id
			and numb.etat_id = numeb.id) as tmp
on affnum.affaire_id = tmp.affaire_id and affnum.numero_id = tmp.numero_associe_id
left join infolica.numero_differe as numdiff on affnum.numero_id = numdiff.numero_id, 
infolica.affaire as aff, infolica.affaire_type as afft, infolica.numero as num, infolica.cadastre as cad, infolica.numero_type as numt, infolica.numero_etat as nume, 
infolica.affaire_numero_type as affnumt
where affnum.affaire_id = aff.id
and afft.id = aff.type_id
and affnum.numero_id = num.id
and num.cadastre_id = cad.id
and num.type_id = numt.id
and num.etat_id = nume.id
and affnum.type_id = affnumt.id
order by numero_base_id, numero_id asc, affaire_date desc
