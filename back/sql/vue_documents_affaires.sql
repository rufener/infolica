create view infolica.v_documents_affaire as
SELECT
	doc.id as id,
	doc.nom as nom,
	doc.chemin as chemin,
	doc.type_id as type_id,
	doct.nom as type_doc,
	doc.affaire_id as affaire_id
FROM
	infolica.document as doc,
	infolica.document_type as doct
WHERE
	doc.type_id = doct.id