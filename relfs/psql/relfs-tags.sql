--
-- tag --
--
CREATE TABLE relfs.tag (
	tag_id         relfs.ID       NOT NULL,
	tag_code       relfs.STR_CODE NOT NULL
);

ALTER TABLE relfs.tag
ADD PRIMARY KEY(tag_id);

ALTER TABLE relfs.tag
ADD UNIQUE(tag_code);

CREATE SEQUENCE relfs.seq_tag_id;

CREATE FUNCTION relfs.get_next_tag_id()
RETURNS relfs.ID AS
$$
SELECT CAST(nextval('relfs.seq_tag_id') AS relfs.ID);
$$
LANGUAGE sql;

CREATE FUNCTION relfs.get_last_tag_id()
RETURNS relfs.ID AS
$$
SELECT CAST(last_value AS relfs.ID)
FROM relfs.seq_tag_id;
$$
LANGUAGE sql;

--
-- tag_inheritance --
--
CREATE TABLE relfs.tag_inheritance (
	generalization_tag_id relfs.ID NOT NULL,
	specialization_tag_id relfs.ID NOT NULL
);

ALTER TABLE relfs.tag_inheritance
ADD PRIMARY KEY(generalization_tag_id, specialization_tag_id);

ALTER TABLE relfs.tag_inheritance
ADD FOREIGN KEY(generalization_tag_id)
REFERENCES relfs.tag;

ALTER TABLE relfs.tag_inheritance
ADD FOREIGN KEY(specialization_tag_id)
REFERENCES relfs.tag;


--
-- get_tag --
--
CREATE FUNCTION relfs.get_tag(relfs.STR_CODE)
RETURNS relfs.ID AS
$$
DECLARE
	v_tag_id relfs.ID;
BEGIN
	SELECT INTO v_tag_id tag_id
	FROM relfs.tag
	WHERE tag_code = $1;

	IF NOT FOUND
	THEN
		v_tag_id := relfs.get_next_tag_id();
		INSERT INTO relfs.tag(tag_id, tag_code)
		VALUES(v_tag_id, upper($1));
	END IF;
	RETURN v_tag_id;
END
$$
LANGUAGE plpgsql;

--
-- add_tag_inheritance --
--
CREATE FUNCTION relfs.add_tag_inheritance(
	generalization_id relfs.STR_CODE,
	specialization_id relfs.STR_CODE
) RETURNS VOID AS
$$
INSERT INTO relfs.tag_inheritance
(generalization_tag_id, specialization_tag_id)
VALUES(relfs.get_tag($1), relfs.get_tag($2))
ON CONFLICT DO NOTHING;
$$
LANGUAGE sql;

--
-- tag_hierarchy --
--
CREATE TABLE relfs.tag_hierarchy (
	generalization_tag_id relfs.ID NOT NULL,
	specialization_tag_id relfs.ID NOT NULL,
	distance              SMALLINT NOT NULL
);

ALTER TABLE relfs.tag_hierarchy
ADD PRIMARY KEY(generalization_tag_id, specialization_tag_id, distance);

--
-- tag_code_hierarchy --
--
CREATE VIEW relfs.tag_code_hierarchy AS
SELECT
	th.generalization_tag_id,
	gt.tag_code AS generalization_tag_code,
	th.specialization_tag_id,
	st.tag_code AS specialization_tag_code,
	distance
FROM relfs.tag_hierarchy th
JOIN relfs.tag gt ON(th.generalization_tag_id = gt.tag_id)
JOIN relfs.tag st ON(th.specialization_tag_id = st.tag_id);

CREATE TYPE relfs._tag_id_code_and_distance AS (
	tag_id         relfs.ID,
	tag_code       relfs.STR_CODE,
	distance       SMALLINT
);

--
-- tag_generalizations --
--
CREATE FUNCTION relfs.tag_generalizations(relfs.STR_CODE)
RETURNS setof relfs._tag_id_code_and_distance AS
$$
SELECT t.tag_id, t.tag_code, th.distance
FROM relfs.tag_hierarchy th
JOIN relfs.tag t ON(th.generalization_tag_id = t.tag_id)
WHERE th.specialization_tag_id = relfs.get_tag($1);
$$
LANGUAGE sql;

--
-- tag_specializations --
--
CREATE FUNCTION relfs.tag_specializations(relfs.STR_CODE)
RETURNS setof relfs._tag_id_code_and_distance AS
$$
SELECT t.tag_id, t.tag_code, th.distance
FROM relfs.tag_hierarchy th
JOIN relfs.tag t ON(th.specialization_tag_id = t.tag_id)
WHERE th.generalization_tag_id = relfs.get_tag($1);
$$
LANGUAGE sql;

--
-- tag modification triggers --
--
CREATE FUNCTION relfs._insert_tag_hierarchy()
RETURNS TRIGGER AS
$$
BEGIN
	INSERT INTO relfs.tag_hierarchy
	(generalization_tag_id, specialization_tag_id, distance)
	VALUES(NEW.tag_id, NEW.tag_id, 0);

	RETURN NEW;
END
$$
LANGUAGE plpgsql;

CREATE TRIGGER insert_tag_hierarchy
AFTER INSERT ON relfs.tag
FOR EACH ROW
EXECUTE PROCEDURE relfs._insert_tag_hierarchy();

--
-- tag inheritance modification triggers --
--
CREATE FUNCTION relfs._insert_tag_inheritance_hierarchy()
RETURNS TRIGGER AS
$$
BEGIN
	INSERT INTO relfs.tag_hierarchy
	SELECT generalization_tag_id, NEW.specialization_tag_id, distance+1
	FROM relfs.tag_hierarchy
	WHERE specialization_tag_id = NEW.generalization_tag_id
	ON CONFLICT DO NOTHING;

	INSERT INTO relfs.tag_hierarchy
	SELECT NEW.generalization_tag_id, specialization_tag_id, distance+1
	FROM relfs.tag_hierarchy
	WHERE generalization_tag_id = NEW.specialization_tag_id
	ON CONFLICT DO NOTHING;

	RETURN NEW;
END
$$
LANGUAGE plpgsql;

CREATE TRIGGER insert_tag_inheritance_hierarchy
AFTER INSERT ON relfs.tag_inheritance
FOR EACH ROW
EXECUTE PROCEDURE relfs._insert_tag_inheritance_hierarchy();

CREATE TRIGGER prevent_tag_inheritance_update
BEFORE UPDATE ON relfs.tag_inheritance
FOR EACH ROW
EXECUTE PROCEDURE relfs._prevent_table_modification();

CREATE TABLE relfs.object_tags (
	object_id         relfs.OBJID    NOT NULL,
	tag_id         relfs.ID NOT NULL
);

ALTER TABLE relfs.object_tags
ADD PRIMARY KEY(object_id, tag_id);



