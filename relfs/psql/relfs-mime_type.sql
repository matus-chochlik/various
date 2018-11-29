CREATE TABLE relfs.object_mime_type (
	object_id         relfs.OBJID    NOT NULL,
	mime_type VARCHAR(32) NOT NULL,
	mime_subtype VARCHAR(32) NOT NULL
);

ALTER TABLE relfs.object_mime_type
ADD PRIMARY KEY(object_id, mime_type, mime_subtype);

INSERT INTO relfs.meta_component
(component_name, associative)
VALUES('mime', TRUE);

INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name, attribute_name)
VALUES('object_mime_type', 'mime_type', 'mime', 'type');

INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name, attribute_name)
VALUES('object_mime_type', 'mime_subtype', 'mime', 'subtype');


