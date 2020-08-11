create view infolica.v_affaires_preavis as
select pr.id as id, pr.affaire_id as affaire_id, ser.service as service, prt.nom as preavis , pr.date_demande as date_demande, pr.date_reponse as date_reponse,
pr.remarque as remarque
from  infolica.service as ser, infolica.preavis as pr
left join infolica.preavis_type as prt on pr.preavis_type_id = prt.id
where pr.service_id = ser.id
order by affaire_id 