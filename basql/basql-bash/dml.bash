function basql_INSERT_INTO()
{
	table="${1}"
	shift

	echo "INSERT INTO $(PREFIXED $(TABLE_NAME ${table}))" "${@}" ";"
}

function basql_INSERT_NAME_DESC()
{
	if [[ "${1}" == "FOR" ]]
	then shift
	fi

	local table="${1}"
	local table_pk_value="${2}"
	local locale_code="${3}"
	local name="${4}"
	local description="${5}"

	echo "--"
	echo "-- NAME_DESC FOR ${table} in ${locale_code}"
	echo "--"
	echo "UPDATE $(PREFIXED $(TABLE_NAME ${table}))"
	echo "SET $(TABLE_PK_NAME name_desc) = coalesce($(TABLE_PK_NAME name_desc), $(PREFIXED get_next_$(TABLE_PK_NAME name_desc))())"
	echo "WHERE $(TABLE_PK_NAME ${table}) = ${table_pk_value};"
	echo
	echo "INSERT INTO $(PREFIXED $(TABLE_NAME name_desc))"
	echo "($(TABLE_PK_NAME name_desc), $(TABLE_PK_NAME locale), name, description)"
	echo "SELECT $(TABLE_PK_NAME name_desc), ${locale_code}, ${name}, ${description}"
	echo "FROM $(PREFIXED $(TABLE_NAME ${table}))"
	echo "WHERE $(TABLE_PK_NAME ${table}) = ${table_pk_value};"
	echo
}

function basql_INSERT_LOCALE()
{
	local locale_code="${1}"
	local name="${2}"
	local description="${3}"

	if basql_is_flag_set HAS_FUNCTION_insert_locale
	then echo
	else
		echo "--"
		echo "-- insert_locale"
		echo "--"
		echo
		echo "CREATE FUNCTION $(PREFIXED insert_locale)($(LOCALE_CODE), $(NAME_STR), $(DESC_STR))"
		echo "RETURNS $(LOCALE_CODE)"
		echo "AS"
		echo "\$\$"
		echo "DECLARE"
		echo "_locale_code ALIAS FOR \$1;"
		echo "_name ALIAS FOR \$2;"
		echo "_description ALIAS FOR \$3;"
		echo "BEGIN"
		echo "INSERT INTO $(PREFIXED $(TABLE_NAME locale))"
		echo "(locale_code, $(TABLE_PK_NAME name_desc))"
		echo "VALUES(_locale_code, $(PREFIXED get_next_$(TABLE_PK_NAME name_desc))());"
		echo
		echo "INSERT INTO $(PREFIXED $(TABLE_NAME name_desc))"
		echo "($(TABLE_PK_NAME name_desc), $(TABLE_PK_NAME locale), name, description)"
		echo "VALUES($(PREFIXED get_last_$(TABLE_PK_NAME name_desc))(), _locale_code, _name, _description);"
		echo
		echo "RETURN _locale_code;"
		echo "END"
		echo "\$\$"
		echo "LANGUAGE plpgsql;"
		echo

		echo "INSERT INTO $(PREFIXED meta_function_result) ("
		echo "	function_catalog, function_schema, function_name, result_kind,"
		echo "	catalog_name, schema_name, table_name, relation_name, column_name"
		echo ") VALUES ("
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'update_locale_name_desc',"
		echo "	'A',"
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME locale)',"
		echo "	'locale', '$(TABLE_PK_NAME locale)'"
		echo ");"

		echo "INSERT INTO $(PREFIXED meta_parameter_column) ("
		echo "	function_catalog, function_schema, function_name, parameter_name,"
		echo "	parameter_kind, ordinal_position,"
		echo "	catalog_name, schema_name, table_name, relation_name, column_name"
		echo ") VALUES ("
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'insert_locale', '$(TABLE_PK_NAME locale)',"
		echo "	'E', 1,"
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME locale)',"
		echo "	'locale', '$(TABLE_PK_NAME locale)'"
		echo ");"

		echo "INSERT INTO $(PREFIXED meta_parameter_column) ("
		echo "	function_catalog, function_schema, function_name, parameter_name,"
		echo "	parameter_kind, ordinal_position,"
		echo "	catalog_name, schema_name, table_name, relation_name, column_name"
		echo ") VALUES ("
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'insert_locale', 'name',"
		echo "	'A', 2,"
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME locale)',"
		echo "	'locale', 'name'"
		echo ");"

		echo "INSERT INTO $(PREFIXED meta_parameter_column) ("
		echo "	function_catalog, function_schema, function_name, parameter_name,"
		echo "	parameter_kind, ordinal_position,"
		echo "	catalog_name, schema_name, table_name, relation_name, column_name"
		echo ") VALUES ("
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'insert_locale', 'description',"
		echo "	'A', 3,"
		echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME locale)',"
		echo "	'locale', 'description'"
		echo ");"

		basql_set_flag HAS_FUNCTION_insert_locale
	fi

	echo "--"
	echo "-- LOCALE ${locale_code}"
	echo "--"
	echo "SELECT $(PREFIXED insert_locale)(${locale_code}, ${name}, ${description});"
	echo
}

function basql_INSERT_ID_ETC()
{
	local table="${1}"
	local id="${2}"
	shift 2

	echo "--"
	echo "-- TYPE ${table}"
	echo "--"

	local name_desc_count=0
	local attrib_count=0
	local attrib_names=( )
	local attrib_values=( )

	while [[ "${1}" != "" ]]
	do
		case "${1}_${2}" in
		WITH_NAME_DESC)
			shift 2
			local locale_code="${1}"
			local name="${2}"
			local description="${3}"
			shift 3

			echo "INSERT INTO $(PREFIXED $(TABLE_NAME name_desc))"
			echo "($(TABLE_PK_NAME name_desc), $(TABLE_PK_NAME locale), name, description)"
			echo "VALUES("
			if [[ ${name_desc_count} -eq 0 ]]
			then echo "	$(PREFIXED get_next_$(TABLE_PK_NAME name_desc))(), "
			else echo "	$(PREFIXED get_last_$(TABLE_PK_NAME name_desc))(), "
			fi
			echo "	${locale_code}, ${name}, ${description}"
			echo ");"
			echo
			let ++name_desc_count
			;;
		WITH_ATTRIBUTE)
			shift 2
			let ++attrib_count
			attrib_names[${attrib_count}]="${1}"
			attrib_values[${attrib_count}]="${2}"
			shift 2
			;;
		*) basql_error "Syntax error '${@}'";;
		esac
	done

	if [[ ${name_desc_count} -eq 0 ]]
	then basql_error "At least one NAME_DESC required for INSERT TYPE"
	fi

	echo "INSERT INTO $(PREFIXED $(TABLE_NAME ${table}))"
	echo -n "($(TABLE_PK_NAME ${table}), $(TABLE_PK_NAME name_desc)"
	for i in $(seq 1 ${attrib_count})
	do echo -n ", ${attrib_names[${i}]}"
	done
	echo ")"
	echo -n "VALUES(${id}, $(PREFIXED get_last_$(TABLE_PK_NAME name_desc))()"
	for i in $(seq 1 ${attrib_count})
	do echo -n ", ${attrib_values[${i}]}"
	done
	echo ");"
	echo
}

function basql_INSERT_COUNTRY()
{
	local code="${1}"
	shift 

	basql_INSERT_ID_ETC "country" "${code}" "${@}"
}

function basql_INSERT_TYPE()
{
	local table="${1}"
	shift 

	basql_INSERT_ID_ETC "${table}" "$(PREFIXED get_next_$(TABLE_PK_NAME ${table}))()" "${@}"
}

function basql_INSERT_GENE_SPEC()
{
	local generalization=""
	local specialization=""
	local temp_expr=""

	while [[ ${#} -gt 0 ]]
	do
		if [[ "${1}_${2}" == "BY_CODE" ]]
		then
			temp_expr="(SELECT $(PREFIXED get_$(TABLE_PK_NAME category))(${3}))"
			shift 3
		elif [[ "${1}" == "LAST" ]]
		then
			temp_expr="($(PREFIXED get_last_$(TABLE_PK_NAME category))())"
			shift
		else temp_expr="${1}"
		fi

		if [[ ${#generalization} -eq 0 ]]
		then generalization="${temp_expr}"
		elif [[ ${#specialization} -eq 0 ]]
		then specialization=${temp_expr}
		else basql_error "Superfluous ${@} after INSERT GENE_SPEC."
		fi
	done

	if [[ ${#generalization} -eq 0 ]]
	then basql_error "Missing generalization expression after INSERT GENE_SPEC."
	elif [[ ${#specialization} -eq 0 ]]
	then basql_error "Missing specialization expression after INSERT GENE_SPEC."
	fi

	echo "INSERT INTO $(PREFIXED $(TABLE_NAME explicit_ontology))"
	echo "($(TABLE_PK_ROLENAME category generalization), $(TABLE_PK_ROLENAME category specialization))"
	echo "VALUES(${generalization}, ${specialization});"
	echo
}

function basql_INSERT_META_SCHEMA()
{
	local schema_name="$(SCHEMA_NAME)"
	echo "--"
	echo "-- META_SCHEMA ${schema_name}"
	echo "--"
	echo "INSERT INTO $(PREFIXED $(TABLE_NAME meta_schema))"
	echo "(catalog_name, schema_name, $(TABLE_PK_NAME name_desc))"
	echo "VALUES('$(DB_NAME)', '${schema_name}', $(PREFIXED get_next_$(TABLE_PK_NAME name_desc))());"
	echo
	
	while [[ ${#} -gt 0 ]]
	do
		if [[ "${1}_${2}" == "WITH_NAME_DESC" ]]
		then
			shift 2
			local locale_code="${1}"
			local name="${2}"
			local description="${3}"

			echo "INSERT INTO $(PREFIXED $(TABLE_NAME name_desc))"
			echo "($(TABLE_PK_NAME name_desc), $(TABLE_PK_NAME locale), name, description)"
			echo "VALUES($(PREFIXED get_last_$(TABLE_PK_NAME name_desc))(), ${locale_code}, ${name}, ${description});"
			echo
			shift 3
		else basql_error "Invalid clause '${1}'"
		fi
	done
	echo
}

function basql_INSERT_META_RELATION()
{
	local relation_name="${1}"
	shift
	echo "--"
	echo "-- META_RELATION ${relation_name}"
	echo "--"
	echo "INSERT INTO $(PREFIXED $(TABLE_NAME meta_relation))"
	echo "(catalog_name, schema_name, table_name, relation_name, $(TABLE_PK_NAME name_desc))"
	echo "VALUES('$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation_name})', '${relation_name}', $(PREFIXED get_next_$(TABLE_PK_NAME name_desc))());"
	echo
	
	while [[ ${#} -gt 0 ]]
	do
		if [[ "${1}_${2}" == "WITH_NAME_DESC" ]]
		then
			shift 2
			local locale_code="${1}"
			local name="${2}"
			local description="${3}"
			shift 3

			echo "INSERT INTO $(PREFIXED $(TABLE_NAME name_desc))"
			echo "($(TABLE_PK_NAME name_desc), $(TABLE_PK_NAME locale), name, description)"
			echo "VALUES($(PREFIXED get_last_$(TABLE_PK_NAME name_desc))(), ${locale_code}, ${name}, ${description});"
			echo
		elif [[ "${1}_${2}" == "IN_GROUP" ]]
		then
			shift 2
			local group_name="${1}"
			shift

			echo "INSERT INTO $(PREFIXED $(TABLE_NAME meta_group_relation))"
			echo "(group_catalog, group_schema, group_name, catalog_name, schema_name, relation_name)"
			echo "VALUES('$(DB_NAME)', '$(SCHEMA_NAME)', '${group_name}', '$(DB_NAME)', '$(SCHEMA_NAME)', '${relation_name}');"
			echo
		else basql_error "Invalid clause '${1}'"
		fi
	done
	echo
}

function basql_INSERT_META_GROUP()
{
	local group_name="${1}"
	shift
	echo "--"
	echo "-- META_GROUP ${group_name}"
	echo "--"
	echo "INSERT INTO $(PREFIXED $(TABLE_NAME meta_group))"
	echo "(catalog_name, schema_name, group_name, $(TABLE_PK_NAME name_desc))"
	echo "VALUES('$(DB_NAME)', '$(SCHEMA_NAME)', '${group_name}', $(PREFIXED get_next_$(TABLE_PK_NAME name_desc))());"
	echo
	
	while [[ ${#} -gt 0 ]]
	do
		if [[ "${1}_${2}" == "WITH_NAME_DESC" ]]
		then
			shift 2
			local locale_code="${1}"
			local name="${2}"
			local description="${3}"

			echo "INSERT INTO $(PREFIXED $(TABLE_NAME name_desc))"
			echo "($(TABLE_PK_NAME name_desc), $(TABLE_PK_NAME locale), name, description)"
			echo "VALUES($(PREFIXED get_last_$(TABLE_PK_NAME name_desc))(), ${locale_code}, ${name}, ${description});"
			echo
			shift 3
		else basql_error "Invalid clause '${1}'"
		fi
	done
	echo
}

function basql_INSERT_META_FOREIGN_COLUMN()
{
	local relation_name="${1}"
	local column_name="${2}"
	local table_name="${3}"
	shift 3

	local has_name_desc=false

	for arg
	do
		if [[ "${arg}" == "NAME_DESC" ]]
		then has_name_desc=true && break
		fi
	done

	echo "--"
	echo "-- META_COLUMN ${relation_name}.${column_name}"
	echo "--"
	echo "INSERT INTO $(PREFIXED $(TABLE_NAME meta_column))"
	echo "(catalog_name, schema_name, table_name, relation_name, column_name,"
	echo " data_type, ordinal_position, is_nullable, $(TABLE_PK_NAME name_desc))"
	echo "SELECT"
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${table_name})', '${relation_name}', '${column_name}',"
	echo "	data_type, ordinal_position, is_nullable = 'YES',"

	if [[ "${has_name_desc}" == "true" ]]
	then echo "	$(PREFIXED get_next_$(TABLE_PK_NAME name_desc))()"
	else
		echo "	(SELECT"
		echo "		$(TABLE_PK_NAME name_desc)"
		echo "		FROM $(PREFIXED $(TABLE_NAME meta_column))"
		echo "		WHERE catalog_name = '$(DB_NAME)'"
		echo "		AND schema_name = '$(SCHEMA_NAME)'"
		echo "		AND table_name = '$(TABLE_NAME ${table_name})'"
		echo "		AND column_name = '${column_name}'"
		echo "	)"
	fi

	echo "FROM information_schema.columns"
	echo "WHERE table_catalog = '$(DB_NAME)'"
	echo "AND table_schema = '$(SCHEMA_NAME)'"
	echo "AND table_name = '$(TABLE_NAME ${table_name})'"
	echo "AND column_name = '${column_name}';"
	echo
	
	while [[ ${#} -gt 0 ]]
	do
		if [[ "${1}_${2}" == "WITH_NAME_DESC" ]]
		then
			shift 2
			local locale_code="${1}"
			local name="${2}"
			local description="${3}"

			echo "INSERT INTO $(PREFIXED $(TABLE_NAME name_desc))"
			echo "($(TABLE_PK_NAME name_desc), $(TABLE_PK_NAME locale), name, description)"
			echo "VALUES($(PREFIXED get_last_$(TABLE_PK_NAME name_desc))(), ${locale_code}, ${name}, ${description});"
			echo
			shift 3
		else basql_error "Invalid clause '${1}'"
		fi
	done
	echo
}

function basql_INSERT_META_COLUMN()
{
	local relation_name="${1}"
	local column_name="${2}"
	shift 2
	basql_INSERT_META_FOREIGN_COLUMN "${relation_name}" "${column_name}" "${relation_name}" "${@}"
}

function basql_INSERT_META_RELATIONSHIP_COLUMN()
{
	parent_table="${1}"
	parent_column="${2}"
	child_table="${3}"
	child_column="${4:-${parent_column}}"
	relship_name="${5:-${parent_table}}"

	if [[ "${child_column}" == "-" ]]
	then child_column="${parent_column}"
	fi

	echo "--"
	echo "-- META_RELATIONSHIP_COLUMN ${child_table}.${child_column} -> ${parent_table}.${parent_column}"
	echo "--"
	echo "INSERT INTO $(PREFIXED $(TABLE_NAME meta_relationship_column))"
	echo "(parent_catalog,parent_schema,parent_table,parent_relation,parent_column"
	echo ", child_catalog, child_schema, child_table, child_relation, child_column"

	if [[ "${relship_name}" != "" ]]
	then echo ", relationship_name"
	fi
	echo ", ordinal_position) VALUES"

	echo "('$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${parent_table})', '${parent_table}', '${parent_column}'"
	echo ",'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${child_table})',  '${child_table}',  '${child_column}'"
	if [[ "${relship_name}" != "" ]]
	then echo ",'${relship_name}'"
	fi
	echo ", coalesce((SELECT ordinal_position "
	echo "	FROM $(PREFIXED meta_column)"
	echo "	WHERE catalog_name = '$(DB_NAME)'"
	echo "	AND schema_name = '$(SCHEMA_NAME)'"
	echo "	AND table_name = '$(TABLE_NAME ${child_table})'"
	echo "  AND column_name = '${child_column}'"
	echo "  ), 1)"
	echo ");"
	echo
}

function basql_INSERT_META_FUNCTION()
{
	local function_name="${1}"
	shift
	echo "--"
	echo "-- META_FUNCTION ${function_name}"
	echo "--"
	echo "INSERT INTO $(PREFIXED $(TABLE_NAME meta_function))"
	echo "(function_catalog, function_schema, function_name, $(TABLE_PK_NAME name_desc))"
	echo "VALUES('$(DB_NAME)', '$(SCHEMA_NAME)', '${function_name}', $(PREFIXED get_next_$(TABLE_PK_NAME name_desc))());"
	echo
	
	while [[ ${#} -gt 0 ]]
	do
		if [[ "${1}_${2}" == "WITH_NAME_DESC" ]]
		then
			shift 2
			local locale_code="${1}"
			local name="${2}"
			local description="${3}"
			shift 3

			echo "INSERT INTO $(PREFIXED $(TABLE_NAME name_desc))"
			echo "($(TABLE_PK_NAME name_desc), $(TABLE_PK_NAME locale), name, description)"
			echo "VALUES($(PREFIXED get_last_$(TABLE_PK_NAME name_desc))(), ${locale_code}, ${name}, ${description});"
			echo
		elif [[ "${1}_${2}" == "WITH_RESULT" ]]
		then
			shift 2
			local result_kind="${1}"
			local relation="${2}"
			local column="${3}"
			shift 3

			echo "INSERT INTO $(PREFIXED $(TABLE_NAME meta_function_result)) ("
			echo "	function_catalog, function_schema, function_name, result_kind,"
			echo "	catalog_name, schema_name, table_name, relation_name, column_name"
			echo ") VALUES ("
			echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '${function_name}', '${result_kind}',"
			echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})',"
			echo "	'${relation}', '${column}'"
			echo ");"
			echo
		elif [[ "${1}_${2}_${3}" == "WITH_PARAMETER_COLUMN" ]]
		then
			shift 3
			local parameter_name="${1}"
			local parameter_kind="${2}"
			local ordinal_position="${3}"
			local relation="${4}"
			local column="${5}"
			shift 5

			echo "INSERT INTO $(PREFIXED $(TABLE_NAME meta_parameter_column)) ("
			echo "	function_catalog, function_schema, function_name, parameter_name,"
			echo "	parameter_kind, ordinal_position,"
			echo "	catalog_name, schema_name, table_name, relation_name, column_name"
			echo ") VALUES ("
			echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '${function_name}', '${parameter_name}',"
			echo "	'${result_kind}', ${ordinal_position},"
			echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})',"
			echo "	'${relation}', '${column}'"
			echo ");"
			echo
		elif [[ "${1}_${2}" == "IN_GROUP" ]]
		then
			shift 2
			local group_name="${1}"
			shift

			echo "INSERT INTO $(PREFIXED $(TABLE_NAME meta_group_function))"
			echo "(group_catalog, group_schema, group_name, catalog_name, schema_name, function_name)"
			echo "VALUES('$(DB_NAME)', '$(SCHEMA_NAME)', '${group_name}', '$(DB_NAME)', '$(SCHEMA_NAME)', '${function_name}');"
			echo
		else basql_error "Invalid clause '${1}'"
		fi
	done
	echo
}


function basql_INSERT_META_OPERATION()
{
	local code="${1}"
	shift
	echo "--"
	echo "-- META_OPERATION ${1}"
	echo "--"
	echo "INSERT INTO $(PREFIXED $(TABLE_NAME meta_operation))"
	echo "(operation_name, $(TABLE_PK_NAME name_desc))"
	echo "VALUES('${code}', $(PREFIXED get_next_$(TABLE_PK_NAME name_desc))());"
	echo
	
	while [[ ${#} -gt 0 ]]
	do
		if [[ "${1}_${2}" == "WITH_NAME_DESC" ]]
		then
			shift 2
			local locale_code="${1}"
			local name="${2}"
			local description="${3}"

			echo "INSERT INTO $(PREFIXED $(TABLE_NAME name_desc))"
			echo "($(TABLE_PK_NAME name_desc), $(TABLE_PK_NAME locale), name, description)"
			echo "VALUES($(PREFIXED get_last_$(TABLE_PK_NAME name_desc))(), ${locale_code}, ${name}, ${description});"
			echo
			shift 3
		else basql_error "Invalid clause '${1}'"
		fi
	done
	echo
}

function basql_SET_ID_SEQUENCE()
{
	relation="${1}"
	value=${2}
	shift 2

	echo "--"
	echo "SELECT setval('$(PREFIXED seq_$(TABLE_PK_NAME ${relation}))', ${value});"
	echo
}
