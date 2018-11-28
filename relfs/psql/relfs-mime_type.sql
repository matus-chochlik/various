CREATE TABLE relfs.object_mime_type (
	object_id         relfs.OBJID    NOT NULL,
	mime_type VARCHAR(32) NOT NULL,
	mime_subtype VARCHAR(32) NOT NULL
);

ALTER TABLE relfs.object_mime_type
ADD PRIMARY KEY(object_id, mime_type, mime_subtype);

INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name, attribute_name)
VALUES('object_mime_type', 'mime_type', 'mime', 'type');

INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name, attribute_name)
VALUES('object_mime_type', 'mime_subtype', 'mime', 'subtype');

CREATE FUNCTION relfs.set_object_mime_type(
	relfs.STRHASH,
	TEXT,
	TEXT
) RETURNS relfs.OBJID
AS
$$
DECLARE
	p_obj_hash ALIAS FOR $1;
	p_mime_type ALIAS FOR $2;
	p_mime_subtype ALIAS FOR $3;
	v_obj_id relfs.OBJID;
BEGIN
	v_obj_id := relfs.get_file_object(p_obj_hash);

	INSERT INTO relfs.object_mime_type
	(object_id, mime_type, mime_subtype)
	VALUES(v_obj_id, p_mime_type, p_mime_subtype)
	ON CONFLICT
	DO NOTHING;

	RETURN v_obj_id;
END
$$
LANGUAGE plpgsql;


