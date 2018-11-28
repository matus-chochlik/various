CREATE TABLE relfs.object_picture_info (
	object_id relfs.OBJID NOT NULL,
	width INTEGER NOT NULL,
	height INTEGER NOT NULL
);

ALTER TABLE relfs.object_picture_info
ADD PRIMARY KEY(object_id);

INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name)
VALUES('object_picture_info', 'width', 'picture');

INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name)
VALUES('object_picture_info', 'height', 'picture');

CREATE VIEW relfs.picture_object
AS
SELECT
	object_id,
	width,
	height,
	width * height AS pixel_count,
	CAST(width AS FLOAT) / CAST(height AS FLOAT) AS aspect_ratio
FROM relfs.object_picture_info;


INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name, mutable)
VALUES('picture_object', 'pixel_count', 'picture', FALSE);

INSERT INTO relfs.meta_component_attribute_mapping
(table_name, column_name, component_name, mutable)
VALUES('picture_object', 'aspect_ratio', 'picture', FALSE);

