CREATE TABLE relfs.meta_component_attribute_mapping (
	key_name NAME NOT NULL DEFAULT 'object_id',
	table_name NAME NOT NULL,
	component_name NAME NULL,
	column_name NAME NOT NULL,
	attribute_name NAME NULL,
	foreign_table_name NAME NULL,
	mutable BOOL NOT NULL DEFAULT TRUE
);

ALTER TABLE relfs.meta_component_attribute_mapping
ADD PRIMARY KEY(table_name, column_name);

CREATE VIEW relfs.meta_component_attribute
AS
SELECT
	key_name,
	table_name,
	coalesce(component_name, table_name) AS component_name,
	column_name,
	coalesce(attribute_name, column_name) as attribute_name,
	foreign_table_name,
	mutable
FROM relfs.meta_component_attribute_mapping;



