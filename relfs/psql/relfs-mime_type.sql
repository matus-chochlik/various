CREATE TABLE relfs.object_mime_type (
	object_id         relfs.OBJID    NOT NULL,
	mime_type VARCHAR(32) NOT NULL,
	mime_subtype VARCHAR(32) NOT NULL
);

ALTER TABLE relfs.object_mime_type
ADD PRIMARY KEY(object_id, mime_type, mime_subtype);

INSERT INTO relfs.meta_table
(table_name, is_associative, is_mutable)
VALUES('object_mime_type', TRUE, TRUE);

INSERT INTO relfs.meta_table_key
(table_name, key_column_name)
VALUES('object_mime_type', 'object_id');

INSERT INTO relfs.meta_table_key
(table_name, key_column_name)
VALUES('object_mime_type', 'mime_type');

INSERT INTO relfs.meta_table_key
(table_name, key_column_name)
VALUES('object_mime_type', 'mime_subtype');

INSERT INTO relfs.meta_component
(component_name)
VALUES('mime');

INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name, attribute_name)
VALUES('object_mime_type', 'mime_type', 'mime', 'type');

INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name, attribute_name)
VALUES('object_mime_type', 'mime_subtype', 'mime', 'subtype');


