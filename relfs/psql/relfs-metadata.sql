CREATE TABLE relfs.meta_table (
	table_name NAME NOT NULL,
	key_column_name NAME NOT NULL DEFAULT 'object_id',
	mutable BOOL NOT NULL,
	associative BOOL NOT NULL
);

ALTER TABLE relfs.meta_table
ADD PRIMARY KEY(table_name);

CREATE TABLE relfs.meta_table_key (
	table_name NAME NOT NULL,
	key_column_name NAME NOT NULL DEFAULT 'object_id'
);

ALTER TABLE relfs.meta_table_key
ADD PRIMARY KEY(table_name, key_column_name);

ALTER TABLE relfs.meta_table_key
ADD FOREIGN KEY(table_name)
REFERENCES relfs.meta_table;

CREATE TABLE relfs.meta_component (
	component_name NAME NOT NULL
);

ALTER TABLE relfs.meta_component
ADD PRIMARY KEY(component_name);

CREATE TABLE relfs.meta_component_attribute_mapping (
	table_name NAME NOT NULL,
	component_name NAME NULL,
	column_name NAME NOT NULL,
	attribute_name NAME NULL,
	foreign_table_name NAME NULL
);

ALTER TABLE relfs.meta_component_attribute_mapping
ADD PRIMARY KEY(table_name, column_name);

ALTER TABLE relfs.meta_component_attribute_mapping
ADD FOREIGN KEY(table_name)
REFERENCES relfs.meta_table;

ALTER TABLE relfs.meta_component_attribute_mapping
ADD FOREIGN KEY(component_name)
REFERENCES relfs.meta_component;

CREATE VIEW relfs.meta_component_attribute
AS
SELECT
	table_name,
	coalesce(component_name, table_name) AS component_name,
	column_name,
	coalesce(attribute_name, column_name) as attribute_name,
	foreign_table_name
FROM relfs.meta_component_attribute_mapping;



