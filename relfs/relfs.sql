DROP SCHEMA relfs CASCADE;

CREATE SCHEMA relfs;

CREATE DOMAIN relfs.OBJID AS BIGINT;
CREATE DOMAIN relfs.STRHASH AS CHAR(64);
CREATE DOMAIN relfs.BINHASH AS BYTEA;

CREATE SEQUENCE relfs.seq_object_id;

CREATE FUNCTION relfs.get_next_object_id()
RETURNS relfs.OBJID
AS $$ SELECT CAST(nextval('relfs.seq_object_id') AS relfs.OBJID); $$
LANGUAGE sql;

CREATE FUNCTION relfs.get_last_object_id()
RETURNS relfs.OBJID
AS
$$ SELECT CAST(last_value AS relfs.OBJID) FROM relfs.seq_object_id; $$
LANGUAGE sql;

CREATE TABLE relfs.file_object (
	object_id         relfs.OBJID    NOT NULL,
	object_bin_hash   relfs.BINHASH  NOT NULL
);

ALTER TABLE relfs.file_object ADD PRIMARY KEY(object_id);
ALTER TABLE relfs.file_object ADD UNIQUE(object_id);

CREATE FUNCTION relfs.to_bin_hash(relfs.STRHASH)
RETURNS relfs.BINHASH
AS $$ SELECT CAST(decode($1, 'hex') AS relfs.BINHASH); $$
LANGUAGE sql;

CREATE FUNCTION relfs.to_str_hash(relfs.BINHASH)
RETURNS relfs.STRHASH
AS $$ SELECT CAST(encode($1, 'hex') AS relfs.STRHASH); $$
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

