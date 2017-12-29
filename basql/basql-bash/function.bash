function basql_CREATE_INSERTER()
{
	if [ "${1}" == "FOR" ]
	then shift
	fi

	local relation="${1}"
	local pk_name="$(TABLE_PK_NAME ${relation})"
	local comma_req=false

	local has_auto_id=false

	echo "--"
	echo "-- insert_${relation}"
	echo "--"
	echo "CREATE FUNCTION $(PREFIXED insert_${relation})("

	if [ "${pk_name}" != "" ]
	then
		if ! TABLE_HAS_AUTO_ID ${relation}
		then
			echo -n "	$(PREFIXED $(TABLE_NAME ${relation})).$(TABLE_PK_NAME ${relation})%TYPE"
			comma_req=true
		fi
	fi

	if basql_is_flag_set TABLE_${relation}_HAS_STR_CODE
	then
		if [[ "${comma_req}" == "true" ]]
		then echo ","
		fi

		echo -n "	$(PREFIXED $(TABLE_NAME ${relation})).str_code%TYPE"
		comma_req=true
	fi

	if basql_is_flag_set TABLE_${relation}_HAS_NAME_DESC
	then
		if [[ "${comma_req}" == "true" ]]
		then echo ","
		fi

		echo "	$(PREFIXED $(TABLE_NAME locale)).$(TABLE_PK_NAME locale)%TYPE,"
		echo "	$(PREFIXED $(TABLE_NAME name_desc)).name%TYPE,"
		echo -n "	$(PREFIXED $(TABLE_NAME name_desc)).description%TYPE"
		comma_req=true
	fi

	for column in $(basql_fetch_key_value TABLE_${relation}_COLUMNS)
	do
		if [[ "${comma_req}" == "true" ]]
		then echo ","
		else echo
		fi
		echo -n "	$(PREFIXED $(TABLE_NAME ${relation})).${column}%TYPE"
		comma_req=true
	done

	echo
	if [ "${pk_name}" != "" ]
	then echo ") RETURNS $(PREFIXED $(TABLE_NAME ${relation})).$(TABLE_PK_NAME ${relation})%TYPE"
	else echo ") RETURNS VOID"
	fi

	echo "AS"
	echo "\$\$"
	echo "DECLARE"

	local pi=1
	
	if [ "${pk_name}" != "" ]
	then
		if TABLE_HAS_AUTO_ID ${relation}
		then echo "	_${pk_name} $(PREFIXED $(TABLE_NAME ${relation})).$(TABLE_PK_NAME ${relation})%TYPE;"
		else echo "	_${pk_name} ALIAS FOR \$${pi};" && let pi++
		fi
	fi

	if basql_is_flag_set TABLE_${relation}_HAS_STR_CODE
	then
		echo "	_str_code ALIAS FOR \$${pi};" && let pi++
	fi

	if basql_is_flag_set TABLE_${relation}_HAS_NAME_DESC
	then
		echo "	_$(TABLE_PK_NAME locale) ALIAS FOR \$${pi};" && let pi++
		echo "	_name ALIAS FOR \$${pi};" && let pi++
		echo "	_description ALIAS FOR \$${pi};" && let pi++
	fi

	for column in $(basql_fetch_key_value TABLE_${relation}_COLUMNS)
	do
		echo "	_${column} ALIAS FOR \$${pi};" && let pi++
	done

	echo "BEGIN"

	if [ "${pk_name}" != "" ]
	then
		if TABLE_HAS_AUTO_ID ${relation}
		then echo "SELECT $(PREFIXED get_next_${pk_name})() INTO _${pk_name};"
		fi
	fi

	if basql_is_flag_set TABLE_${relation}_HAS_NAME_DESC
	then
		echo
		echo "INSERT INTO $(PREFIXED name_desc) ("
		echo "	$(TABLE_PK_NAME name_desc),"
		echo "	$(TABLE_PK_NAME locale),"
		echo "	name,"
		echo "	description"
		echo ") VALUES ("
		echo "	$(PREFIXED get_next_$(TABLE_PK_NAME name_desc))(),"
		echo "	_$(TABLE_PK_NAME locale),"
		echo "	_name,"
		echo "	_description"
		echo ");"
	fi

	echo
	echo "INSERT INTO $(PREFIXED $(TABLE_NAME ${relation})) ("

	comma_req=false

	if [ "${pk_name}" != "" ]
	then echo -n "	${pk_name}" && comma_req=true
	fi

	if basql_is_flag_set TABLE_${relation}_HAS_STR_CODE
	then
		if [[ "${comma_req}" == "true" ]]
		then echo ","
		else echo
		fi
		echo -n "	str_code"
		comma_req=true
	fi

	if basql_is_flag_set TABLE_${relation}_HAS_NAME_DESC
	then
		if [[ "${comma_req}" == "true" ]]
		then echo ","
		else echo
		fi
		echo -n "	$(TABLE_PK_NAME name_desc)"
		comma_req=true
	fi

	if basql_is_flag_set TABLE_${relation}_HAS_HISTORY
	then
		if [[ "${comma_req}" == "true" ]]
		then echo ","
		else echo
		fi
		echo -n "	$(TABLE_HISTORY_COLNAME ${relation})"
		comma_req=true
	fi

	for column in $(basql_fetch_key_value TABLE_${relation}_COLUMNS)
	do
		if [[ "${comma_req}" == "true" ]]
		then echo ","
		else echo
		fi
		echo -n "	${column}"
		comma_req=true
	done

	echo
	echo ") VALUES ("

	comma_req=false

	if [ "${pk_name}" != "" ]
	then echo -n "	_${pk_name}" && comma_req=true
	fi

	if basql_is_flag_set TABLE_${relation}_HAS_STR_CODE
	then
		if [[ "${comma_req}" == "true" ]]
		then echo ","
		else echo
		fi
		echo -n "	_str_code"
		comma_req=true
	fi

	if basql_is_flag_set TABLE_${relation}_HAS_NAME_DESC
	then
		if [[ "${comma_req}" == "true" ]]
		then echo ","
		else echo
		fi
		echo -n "	$(PREFIXED get_last_$(TABLE_PK_NAME name_desc))()"
		comma_req=true
	fi

	if basql_is_flag_set TABLE_${relation}_HAS_HISTORY
	then
		if [[ "${comma_req}" == "true" ]]
		then echo ","
		else echo
		fi
		echo -n "	CURRENT_DATE"
		comma_req=true
	fi

	for column in $(basql_fetch_key_value TABLE_${relation}_COLUMNS)
	do
		if [[ "${comma_req}" == "true" ]]
		then echo ","
		else echo
		fi
		echo -n "	_${column}"
		comma_req=true
	done

	echo
	echo ");"

	echo
	if [ "${pk_name}" != "" ]
	then echo "RETURN _${pk_name};"
	fi

	echo "END"
	echo "\$\$"
	echo "LANGUAGE plpgsql;"
	echo

	echo "INSERT INTO $(PREFIXED meta_function_result) ("
	echo "	function_catalog, function_schema, function_name, result_kind,"
	echo "	catalog_name, schema_name, table_name, relation_name, column_name"
	echo ") VALUES ("
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'insert_${relation}',"
	if [ "${pk_name}" != "" ]
	then
		echo "	'N',"
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})',"
		echo "	'${relation}', '${pk_name}'"
	else
		echo "	NULL, NULL, NULL, NULL, NULL, NULL"
	fi
	echo ");"

	pi=1

	if [ "${pk_name}" != "" ]
	then
		if ! TABLE_HAS_AUTO_ID ${relation}
		then
			echo "INSERT INTO $(PREFIXED meta_parameter_column) ("
			echo "	function_catalog, function_schema, function_name, parameter_name,"
			echo "	parameter_kind, ordinal_position,"
			echo "	catalog_name, schema_name, table_name, relation_name, column_name"
			echo ") VALUES ("
			echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'insert_${relation}', '${pk_name}',"
			echo "	'U', ${pi},"
			echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})',"
			echo "	'${relation}', '${pk_name}'"
			echo ");"
			let pi++
		fi
	fi

	if basql_is_flag_set TABLE_${relation}_HAS_STR_CODE
	then
		echo "INSERT INTO $(PREFIXED meta_parameter_column) ("
		echo "	function_catalog, function_schema, function_name, parameter_name,"
		echo "	parameter_kind, ordinal_position,"
		echo "	catalog_name, schema_name, table_name, relation_name, column_name"
		echo ") VALUES ("
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'insert_${relation}', 'str_code',"
		echo "	'U', ${pi},"
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})',"
		echo "	'${relation}', 'str_code'"
		echo ");"
		let pi++
	fi

	if basql_is_flag_set TABLE_${relation}_HAS_NAME_DESC
	then
		echo "INSERT INTO $(PREFIXED meta_parameter_column) ("
		echo "	function_catalog, function_schema, function_name, parameter_name,"
		echo "	parameter_kind, ordinal_position,"
		echo "	catalog_name, schema_name, table_name, relation_name, column_name"
		echo ") VALUES ("
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'insert_${relation}', '$(TABLE_PK_NAME locale)',"
		echo "	'E', ${pi},"
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME locale)',"
		echo "	'locale', '$(TABLE_PK_NAME locale)'"
		echo ");"
		let pi++

		echo "INSERT INTO $(PREFIXED meta_parameter_column) ("
		echo "	function_catalog, function_schema, function_name, parameter_name,"
		echo "	parameter_kind, ordinal_position,"
		echo "	catalog_name, schema_name, table_name, relation_name, column_name"
		echo ") VALUES ("
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'insert_${relation}', 'name',"
		echo "	'A', ${pi},"
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})',"
		echo "	'${relation}', 'name'"
		echo ");"
		let pi++

		echo "INSERT INTO $(PREFIXED meta_parameter_column) ("
		echo "	function_catalog, function_schema, function_name, parameter_name,"
		echo "	parameter_kind, ordinal_position,"
		echo "	catalog_name, schema_name, table_name, relation_name, column_name"
		echo ") VALUES ("
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'insert_${relation}', 'description',"
		echo "	'A', ${pi},"
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})',"
		echo "	'${relation}', 'description'"
		echo ");"
		let pi++
	fi

	for column in $(basql_fetch_key_value TABLE_${relation}_COLUMNS)
	do
		ref_table="$(basql_fetch_key_value TABLE_${relation}_${column}_REF_TABLE)"
		ref_column="$(basql_fetch_key_value TABLE_${relation}_${column}_REF_COLUMN)"

		echo "INSERT INTO $(PREFIXED meta_parameter_column) ("
		echo "	function_catalog, function_schema, function_name, parameter_name,"
		echo "	parameter_kind, ordinal_position,"
		echo "	catalog_name, schema_name, table_name, relation_name, column_name"
		echo ") VALUES ("
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'insert_${relation}', '${column}',"

		if [[ "${ref_table}" == "" ]]
		then echo "	'A', ${pi},"
		else echo "	'E', ${pi},"
		fi
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})',"
		echo "	'${relation}', '${column}'"
		echo ");"
		let pi++
	done

	echo "INSERT INTO $(PREFIXED meta_function_relation_op) ("
	echo "	function_catalog, function_schema, function_name,"
	echo "	operation_name,"
	echo "	catalog_name, schema_name, table_name, relation_name"
	echo ") VALUES ("
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'insert_${relation}',"
	echo "	'INSERT',"
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})', '${relation}'"
	echo ");"

	echo "INSERT INTO $(PREFIXED meta_function_relation_op) ("
	echo "	function_catalog, function_schema, function_name,"
	echo "	operation_name,"
	echo "	catalog_name, schema_name, table_name, relation_name"
	echo ") VALUES ("
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'insert_${relation}',"
	echo "	'INSERT',"
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME name_desc)', 'name_desc'"
	echo ");"
}

function basql_CREATE_UPDATERS()
{
	if [ "${1}" == "FOR" ]
	then shift
	fi

	local relation="${1}"
	local pk_name="$(TABLE_PK_NAME ${relation})"
	local comma_req=false
 
	if basql_is_flag_set TABLE_${relation}_HAS_NAME_DESC
	then
		name_desc_pk="$(TABLE_PK_NAME name_desc)"
		echo "--"
		echo "-- update_${relation}_name_desc"
		echo "--"
		echo "CREATE FUNCTION $(PREFIXED update_${relation}_name_desc)("
		echo "	$(PREFIXED $(TABLE_NAME ${relation})).$(TABLE_PK_NAME ${relation})%TYPE,"
		echo "	$(PREFIXED $(TABLE_NAME locale)).$(TABLE_PK_NAME locale)%TYPE,"
		echo "	$(PREFIXED $(TABLE_NAME name_desc)).name%TYPE,"
		echo "	$(PREFIXED $(TABLE_NAME name_desc)).description%TYPE"
		echo ") RETURNS $(PREFIXED $(TABLE_NAME name_desc)).$(TABLE_PK_NAME name_desc)%TYPE"
		echo "AS"
		echo "\$\$"
		echo "DECLARE"
		echo "	_${name_desc_pk} $(TABLE_PK_TYPE name_desc);"
		echo "	_${pk_name} ALIAS FOR \$1;"
		echo "	_$(TABLE_PK_NAME locale) ALIAS FOR \$2;"
		echo "	_name ALIAS FOR \$3;"
		echo "	_description ALIAS FOR \$4;"
		echo "BEGIN"
		echo "_${name_desc_pk} := ("
		echo "	SELECT ${name_desc_pk}"
		echo "	FROM $(PREFIXED $(TABLE_NAME ${relation}))"
		echo "	WHERE ${pk_name} = _${pk_name}"
		echo ");"
		echo "IF EXISTS ("
		echo "	SELECT 1"
		echo "	FROM $(PREFIXED name_desc)"
		echo "	JOIN $(PREFIXED ${relation})"
		echo "	USING(${name_desc_pk})"
		echo "	WHERE $(TABLE_PK_NAME locale) = _$(TABLE_PK_NAME locale)"
		echo "	AND ${name_desc_pk} = _${name_desc_pk}"
		echo ") THEN"
		echo "	UPDATE $(PREFIXED $(TABLE_NAME name_desc))"
		echo "	SET name = _name, description = _description"
		echo "	WHERE $(TABLE_PK_NAME locale) = _$(TABLE_PK_NAME locale)"
		echo "	AND ${name_desc_pk} = _${name_desc_pk};"
		echo "ELSE"
		echo "	IF _${name_desc_pk} IS NULL"
		echo "	THEN _${name_desc_pk} := $(PREFIXED get_next_${name_desc_pk})();"
		echo "	END IF;"
		echo "	INSERT INTO $(PREFIXED $(TABLE_NAME name_desc)) ("
		echo "		${name_desc_pk},"
		echo "		$(TABLE_PK_NAME locale),"
		echo "		name,"
		echo "		description"
		echo "	) VALUES ("
		echo "		_${name_desc_pk},"
		echo "		_$(TABLE_PK_NAME locale),"
		echo "		_name, _description"
		echo "	);"
		echo "	UPDATE $(PREFIXED $(TABLE_NAME ${relation}))"
		echo "	SET ${name_desc_pk} = _${name_desc_pk}"
		echo "	WHERE ${pk_name} = _${pk_name};"
		echo "END IF;"
		echo "RETURN _${name_desc_pk};"
		echo "END"
		echo "\$\$"
		echo "LANGUAGE plpgsql;"
		echo

		echo "INSERT INTO $(PREFIXED meta_function_result) ("
		echo "	function_catalog, function_schema, function_name, result_kind,"
		echo "	catalog_name, schema_name, table_name, relation_name, column_name"
		echo ") VALUES ("
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'update_${relation}_name_desc',"
		echo "	'A',"
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME name_desc)',"
		echo "	'name_desc', '${name_desc_pk}'"
		echo ");"

		echo "INSERT INTO $(PREFIXED meta_parameter_column) ("
		echo "	function_catalog, function_schema, function_name, parameter_name,"
		echo "	 parameter_kind, ordinal_position,"
		echo "	catalog_name, schema_name, table_name, relation_name, column_name"
		echo ") VALUES ("
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'update_${relation}_name_desc', '${pk_name}',"
		echo "	'E', 1,"
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})',"
		echo "	'${relation}', '$(TABLE_PK_NAME ${relation})'"
		echo ");"

		echo "INSERT INTO $(PREFIXED meta_parameter_column) ("
		echo "	function_catalog, function_schema, function_name, parameter_name,"
		echo "	parameter_kind, ordinal_position,"
		echo "	catalog_name, schema_name, table_name, relation_name, column_name"
		echo ") VALUES ("
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'update_${relation}_name_desc', '$(TABLE_PK_NAME locale)',"
		echo "	'E', 2,"
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME locale)',"
		echo "	'locale', '$(TABLE_PK_NAME locale)'"
		echo ");"

		echo "INSERT INTO $(PREFIXED meta_parameter_column) ("
		echo "	function_catalog, function_schema, function_name, parameter_name,"
		echo "	parameter_kind, ordinal_position,"
		echo "	catalog_name, schema_name, table_name, relation_name, column_name"
		echo ") VALUES ("
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'update_${relation}_name_desc', 'name',"
		echo "	'A', 3,"
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})',"
		echo "	'${relation}', 'name'"
		echo ");"

		echo "INSERT INTO $(PREFIXED meta_parameter_column) ("
		echo "	function_catalog, function_schema, function_name, parameter_name,"
		echo "	parameter_kind, ordinal_position,"
		echo "	catalog_name, schema_name, table_name, relation_name, column_name"
		echo ") VALUES ("
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'update_${relation}_name_desc', 'description',"
		echo "	'A', 4,"
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})',"
		echo "	'${relation}', 'description'"
		echo ");"
	fi

	echo "INSERT INTO $(PREFIXED meta_function_relation_op) ("
	echo "	function_catalog, function_schema, function_name,"
	echo "	operation_name,"
	echo "	catalog_name, schema_name, table_name, relation_name"
	echo ") VALUES ("
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'update_${relation}_name_desc',"
	echo "	'INSERT',"
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME name_desc)', 'name_desc'"
	echo ");"

	echo "INSERT INTO $(PREFIXED meta_function_relation_op) ("
	echo "	function_catalog, function_schema, function_name,"
	echo "	operation_name,"
	echo "	catalog_name, schema_name, table_name, relation_name"
	echo ") VALUES ("
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'update_${relation}_name_desc',"
	echo "	'UPDATE',"
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME name_desc)', 'name_desc'"
	echo ");"

}

function basql_CREATE_DELETERS()
{
	local relation="${1}"
}

