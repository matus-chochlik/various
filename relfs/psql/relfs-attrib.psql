CREATE TABLE relfs.attribute_kind (
	attribute_kind_code relfs.STR_CODE NOT NULL
);

ALTER TABLE relfs.attribute_kind
ADD PRIMARY KEY(attribute_kind_code);

CREATE TABLE relfs.attribute_type (
	attribute_type_code relfs.STR_CODE NOT NULL,
	attribute_kind_code relfs.STR_CODE NOT NULL
);

ALTER TABLE relfs.attribute_type
ADD PRIMARY KEY(attribute_type_code);

ALTER TABLE relfs.attribute_type
ADD FOREIGN KEY(attribute_kind_code)
REFERENCES relfs.attribute_kind;


INSERT INTO relfs.attribute_kind VALUES('STRING');

CREATE TABLE relfs.object_attribute_string (
	object_id relfs.OBJID NOT NULL,
	attribute_type_code relfs.STR_CODE NOT NULL,
	value_order relfs.LIST_INDEX NOT NULL,
	value TEXT NOT NULL
);

ALTER TABLE relfs.object_attribute_string
ADD PRIMARY KEY(object_id, attribute_type_code, value_order);

