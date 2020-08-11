update 
	infolica.numero_relation
set 
	affaire_id = tmp2.aff_id
from (
	select 
		tmp.numrel_id,
		tmp.aff_id
	from (
		select 
			numrel.id as numrel_id,
			numrel.numero_id_base as num_base_id,
			numrel.numero_id_associe as num_associe_id,
			affnum_base.affaire_id as aff_id
		from 
			infolica.affaire_numero as affnum_base,
			infolica.affaire_numero as affnum_associe,
			infolica.numero_relation as numrel
		where
			numrel.numero_id_base = affnum_base.numero_id
			and numrel.numero_id_associe = affnum_associe.numero_id
			and affnum_base.affaire_id = affnum_associe.affaire_id	
			and numrel.numero_id_base != 39992
			and numrel.numero_id_associe != 39992
			and numrel.affaire_id is null
		group by
			numrel_id ,
			num_base_id, 
			num_associe_id, 
			aff_id
		order by
			numrel_id
		) as tmp
	where
		tmp.numrel_id not in (
								select 
									tmp.numrel_id
								from (
									select 
										numrel.id as numrel_id,
										numrel.numero_id_base as num_base_id,
										numrel.numero_id_associe as num_associe_id,
										affnum_base.affaire_id as aff_id
									from 
										infolica.affaire_numero as affnum_base,
										infolica.affaire_numero as affnum_associe,
										infolica.numero_relation as numrel
									where
										numrel.numero_id_base = affnum_base.numero_id
										and numrel.numero_id_associe = affnum_associe.numero_id
										and affnum_base.affaire_id = affnum_associe.affaire_id	
										and numrel.numero_id_base != 39992
										and numrel.numero_id_associe != 39992
										and numrel.affaire_id is null
									group by
										numrel_id ,
										num_base_id, 
										num_associe_id, 
										aff_id
									order by
										numrel_id
									) as tmp
								group by
									tmp.numrel_id
								having 
									count(tmp.numrel_id) > 1
							  )
	) as tmp2
where infolica.numero_relation.id = tmp2.numrel_id