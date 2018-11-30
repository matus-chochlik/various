CREATE SEQUENCE relfs.seq_object_id;

CREATE FUNCTION relfs.get_next_object_id()
RETURNS relfs.OBJID
AS
$$
SELECT CAST(nextval('relfs.seq_object_id') AS relfs.OBJID);
$$
LANGUAGE sql;

CREATE FUNCTION relfs.get_last_object_id()
RETURNS relfs.OBJID
AS
$$
SELECT CAST(last_value AS relfs.OBJID)
FROM relfs.seq_object_id;
$$
LANGUAGE sql;

CREATE TABLE relfs.file_object (
	object_id         relfs.OBJID    NOT NULL,
	object_bin_hash   relfs.BINHASH  NOT NULL,
	object_date	      TIMESTAMP WITHOUT TIME ZONE,
	size_bytes		  INTEGER,
	display_name      TEXT,
	extensions        TEXT
);

ALTER TABLE relfs.file_object
ADD PRIMARY KEY(object_id);

ALTER TABLE relfs.file_object
ADD UNIQUE(object_bin_hash);


INSERT INTO relfs.meta_table
(table_name, is_root, is_mutable)
VALUES('file_object', TRUE, TRUE);

INSERT INTO relfs.meta_component
(component_name)
VALUES('file');


INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name, attribute_name)
VALUES('file_object', 'object_bin_hash', 'file', 'hash');

INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name, attribute_name)
VALUES('file_object', 'size_bytes', 'file', 'size');

INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name, attribute_name)
VALUES('file_object', 'object_date', 'file', 'date');

INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name)
VALUES('file_object', 'display_name', 'file');

INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name)
VALUES('file_object', 'extensions', 'file');

CREATE FUNCTION relfs._fill_file_object_id()
RETURNS TRIGGER AS
$$
BEGIN
	NEW.object_id = coalesce(NEW.object_id, relfs.get_next_object_id());
	RETURN NEW;
END
$$
LANGUAGE plpgsql;

CREATE TRIGGER fill_object_id
BEFORE INSERT ON relfs.file_object
FOR EACH ROW
EXECUTE PROCEDURE relfs._fill_file_object_id();


CREATE FUNCTION relfs.to_bin_hash(relfs.STRHASH)
RETURNS relfs.BINHASH
AS
$$
SELECT CAST(decode($1, 'hex') AS relfs.BINHASH);
$$
LANGUAGE sql;

CREATE FUNCTION relfs.to_str_hash(relfs.BINHASH)
RETURNS relfs.STRHASH
AS
$$
SELECT CAST(encode($1, 'hex') AS relfs.STRHASH);
$$
LANGUAGE sql;

CREATE FUNCTION relfs.get_file_object(relfs.STRHASH)
RETURNS relfs.OBJID
AS
$$
DECLARE
	v_bin_hash relfs.BINHASH;
	v_object_id relfs.OBJID;
BEGIN
	SELECT INTO v_bin_hash relfs.to_bin_hash($1);
	SELECT INTO v_object_id object_id
	FROM relfs.file_object
	WHERE object_bin_hash = v_bin_hash;

	IF NOT FOUND
	THEN
		v_object_id := relfs.get_next_object_id();
		INSERT INTO relfs.file_object (object_id, object_bin_hash)
		VALUES(v_object_id, v_bin_hash);
	END IF;
	RETURN v_object_id;
END
$$
LANGUAGE plpgsql;


