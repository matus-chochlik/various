function TABLE_PK_NAME()
{
	basql_fetch_key_value TABLE_${1}_PK_NAME
}

function TABLE_PK_ROLENAME()
{
	pk_name="$(basql_fetch_key_value TABLE_${1}_PK_NAME)"
	echo "${2}${pk_name#${1}}"
}

function TABLE_PK_TYPE()
{
	basql_fetch_key_value TABLE_${1}_PK_TYPE "$(basql_fetch_key_value COLUMN_$(TABLE_PK_NAME ${1})_TYPE)"
}

function TABLE_COLUMN_TYPE()
{
	basql_fetch_key_value TABLE_${1}_${2}_TYPE "${3}"
}

function TABLE_PK_KIND()
{
	basql_fetch_key_value TABLE_${1}_PK_KIND
}

function TABLE_NAME()
{
	basql_fetch_key_value TABLE_${1}_NAME ${1}
}

function TABLE_CAT_CODE()
{
	basql_fetch_key_value TABLE_${1}_CAT_CODE
}

function TABLE_HAS_AUTO_ID()
{
	if basql_is_flag_set TABLE_${1}_HAS_AUTO_ID
	then return 0
	elif basql_is_flag_set COLUMN_$(TABLE_PK_NAME ${1})_HAS_ID_SEQ
	then return 0
	else return 1
	fi
}

function basql_TABLE_WITH_PRIMARY_KEY()
{
	echo "ALTER TABLE $(PREFIXED ${1})"
	echo "ADD COLUMN ${1}_${2} $(${3} ${1})"
	echo "NOT NULL PRIMARY KEY;"
	echo
	basql_store_key_value "TABLE_${1}_PK_NAME" "${1}_${2}"
	basql_store_key_value "TABLE_${1}_PK_TYPE" "$(${3} ${1})"
	basql_store_key_value "TABLE_${1}_PK_KIND" "${2}"
	basql_store_key_value "COLUMN_${1}_${2}_TYPE" "$(${3} ${1})"
}

function basql_TABLE_WITH_WEAK_KEY()
{
	echo "ALTER TABLE $(PREFIXED ${1})"
	echo "ADD COLUMN ${1}_${2} $(${3} ${1})"
	echo "NOT NULL;"
	echo
	basql_store_key_value "TABLE_${1}_PK_NAME" "${1}_${2}"
	basql_store_key_value "TABLE_${1}_PK_TYPE" "$(${3} ${1})"
	basql_store_key_value "TABLE_${1}_PK_KIND" "${2}"
	basql_store_key_value "COLUMN_${1}_${2}_TYPE" "$(${3} ${1})"
}

function basql_TABLE_WITH_SEQ_ID_GEN()
{
	echo "CREATE SEQUENCE $(PREFIXED seq_${1}_${2});"
	echo "CREATE FUNCTION $(PREFIXED get_next_${1}_${2})()"
	echo "RETURNS $(${3}) AS"
	echo "\$\$"
	echo "SELECT CAST(nextval('$(PREFIXED seq_${1}_${2})') AS $(${3}))"
	echo "\$\$"
	echo "LANGUAGE SQL;"
	echo
	echo "CREATE FUNCTION $(PREFIXED get_last_${1}_${2})()"
	echo "RETURNS $(${3}) AS"
	echo "\$\$"
	echo "SELECT CAST(last_value AS $(${3})) FROM $(PREFIXED seq_${1}_${2})"
	echo "\$\$"
	echo "LANGUAGE SQL;"
	echo
	basql_set_flag TABLE_${1}_HAS_AUTO_ID
	basql_set_flag COLUMN_${1}_${2}_HAS_ID_SEQ

	basql_append_key_value TABLES_WITH_ID_SEQUENCE "${1}"
}

function basql_TABLE_WITH_MAX_ID_GEN()
{
	echo "CREATE FUNCTION $(PREFIXED get_next_${1}_${2})()"
	echo "RETURNS $(${3}) AS"
	echo "\$\$"
	echo "SELECT CAST(coalesce(max(${1}_${2})+1, 1) AS $(${3}))"
	echo "FROM $(PREFIXED ${1})"
	echo "\$\$"
	echo "LANGUAGE SQL;"
	echo
	echo "CREATE FUNCTION $(PREFIXED get_last_${1}_${2})()"
	echo "RETURNS $(${3}) AS"
	echo "\$\$"
	echo "SELECT CAST(coalesce(max(${1}_${2}), 1) AS $(${3}))"
	echo "FROM $(PREFIXED ${1})"
	echo "\$\$"
	echo "LANGUAGE SQL;"
	echo
	basql_set_flag TABLE_${1}_HAS_AUTO_ID
	basql_set_flag COLUMN_${1}_${2}_HAS_ID_SEQ
}

function basql_TABLE_WITH_UID()
{
	basql_TABLE_WITH_PRIMARY_KEY "${1}" id UID
	basql_TABLE_WITH_SEQ_ID_GEN "${1}" id UID
}

function basql_TABLE_WITH_WEAK_UID()
{
	basql_TABLE_WITH_WEAK_KEY "${1}" id UID
	basql_TABLE_WITH_SEQ_ID_GEN "${1}" id UID
}

function basql_TABLE_WITH_ID()
{
	basql_TABLE_WITH_PRIMARY_KEY "${1}" id ID
	basql_TABLE_WITH_MAX_ID_GEN "${1}" id ID
}

function basql_TABLE_WITH_WEAK_ID()
{
	basql_TABLE_WITH_WEAK_KEY "${1}" id ID
	basql_TABLE_WITH_SEQ_ID_GEN "${1}" id ID
}

function basql_TABLE_WITH_SID()
{
	basql_TABLE_WITH_PRIMARY_KEY "${1}" id SID
	basql_TABLE_WITH_MAX_ID_GEN "${1}" id SID
}

function basql_TABLE_WITH_STR_CODE()
{
	relation="${1}"
	shift
	if [[ "${1}" =~ ^[0-9]+$ ]]
	then
		length="${1}"
		shift
	fi

	basql_store_key_value "TABLE_${relation}_CAT_CODE" "str_code"

	echo "ALTER TABLE $(PREFIXED ${relation})"
	echo "ADD COLUMN str_code $(STR_CODE ${length})"
	echo "NOT NULL;"
	echo
	echo "CREATE FUNCTION $(PREFIXED get_${relation})($(STR_CODE ${length}))"
	echo "RETURNS $(TABLE_PK_TYPE ${relation}) AS"
	echo "\$\$"
	echo "SELECT $(TABLE_PK_NAME ${relation})"
	echo "FROM $(PREFIXED ${relation})"
	echo "WHERE str_code = \$1"
	echo "\$\$"
	echo "LANGUAGE SQL"
	echo "STABLE"
	echo "RETURNS NULL ON NULL INPUT;"
	echo

	echo "INSERT INTO $(PREFIXED meta_function_result) ("
	echo "	function_catalog, function_schema, function_name, result_kind,"
	echo "	catalog_name, schema_name, table_name, relation_name, column_name"
	echo ") VALUES ("
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'get_${relation}',"
	echo "	'E',"
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})',"
	echo "	'${relation}', '$(TABLE_PK_NAME ${relation})'"
	echo ");"

	echo "INSERT INTO $(PREFIXED meta_parameter_column) ("
	echo "	function_catalog, function_schema, function_name, parameter_name,"
	echo "	 parameter_kind, ordinal_position,"
	echo "	catalog_name, schema_name, table_name, relation_name, column_name"
	echo ") VALUES ("
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'get_${relation}', 'str_code',"
	echo "	'E', 1,"
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})',"
	echo "	'${relation}', 'str_code'"
	echo ");"

	echo "INSERT INTO $(PREFIXED meta_function_relation_op) ("
	echo "	function_catalog, function_schema, function_name,"
	echo "	operation_name,"
	echo "	catalog_name, schema_name, table_name, relation_name"
	echo ") VALUES ("
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', 'get_${relation}',"
	echo "	'SELECT',"
	echo "	'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${relation})', '${relation}'"
	echo ");"

	basql_set_flag TABLE_${relation}_HAS_STR_CODE
	basql_store_key_value "TABLE_${relation}_str_code_TYPE" "$(STR_CODE ${length})"
}

function basql_TABLE_WITH_NAME_DESC()
{
	table="${1}"
	echo "ALTER TABLE $(PREFIXED ${table})"
	echo "ADD COLUMN $(TABLE_PK_NAME name_desc) $(TABLE_PK_TYPE name_desc) NOT NULL;"
	echo
	echo "ALTER TABLE $(PREFIXED ${table})"
	echo "RENAME TO _${table}_data;"
	echo
	echo "CREATE VIEW $(PREFIXED ${table}) AS"
	echo "SELECT td.*, coalesce(nd1.name, nd2.name) AS name, coalesce(nd1.description, nd2.description) AS description"
	echo "FROM $(PREFIXED _${table}_data) td"
	echo "LEFT OUTER JOIN $(PREFIXED current_user_name_desc) nd1 USING($(TABLE_PK_NAME name_desc))"
	echo "LEFT OUTER JOIN $(PREFIXED fallback_name_desc) nd2 USING($(TABLE_PK_NAME name_desc));"
	echo
	basql_store_key_value "TABLE_${table}_NAME" "_${table}_data"

	echo "INSERT INTO $(PREFIXED meta_relationship_column)"
	echo "(parent_catalog,parent_schema,parent_table,parent_relation,parent_column"
	echo ", child_catalog, child_schema, child_table, child_relation, child_column"
	echo ", relationship_name, ordinal_position) VALUES"
	echo "('$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME name_desc)', 'name_desc', '$(TABLE_PK_NAME name_desc)'"
	echo ",'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${table})',  '${table}', '$(TABLE_PK_NAME name_desc)'"
	echo ",'name_desc', 1);"
	echo

	if [[ ! ${table} =~ meta_* ]]
	then
		if [[ "$(TABLE_PK_NAME ${table})" != "" ]]
		then
			echo "CREATE FUNCTION $(PREFIXED name_desc_of_$(SCHEMA_NAME)_${table})()"
			echo "RETURNS SETOF $(PREFIXED record_name_desc)"
			echo "AS"
			echo '$$'
			echo "SELECT CAST($(TABLE_PK_NAME ${table}) AS TEXT) id, name, description"
			echo "FROM $(PREFIXED ${table});"
			echo '$$'
			echo 'LANGUAGE SQL;'
			echo
		fi
	fi

	basql_set_flag TABLE_${1}_HAS_NAME_DESC
}

function basql_TABLE_WITH_CATEGORY()
{
	table="${1}"
	cat_code_col="${2}"
	shift 2

	if [[ "${cat_code_col}" != "" ]]
	then cat_code_expr="upper('${table}')||'.'||NEW.${cat_code_col}"
	elif [[ "$(TABLE_CAT_CODE ${table})" != "" ]]
	then cat_code_expr="upper('${table}')||'.'||NEW.$(TABLE_CAT_CODE ${table})"
	elif [[ "${table}" == "meta_group" ]]
	then cat_code_expr="'GROUP.'||upper(NEW.group_name)"
	elif [[ "${table}" == "meta_relation" ]]
	then cat_code_expr="'RELATION.'||upper(NEW.relation_name)"
	elif [[ "${table}" == "meta_column" ]]
	then cat_code_expr="'COLUMN.'||upper(NEW.relation_name)||'.'||upper(NEW.column_name)"
	else cat_code_expr="upper('${table}')||'.'||NEW.$(TABLE_PK_NAME ${table})"
	fi

	shift
	echo "ALTER TABLE $(PREFIXED $(TABLE_NAME ${table}))"
	echo "ADD COLUMN $(TABLE_PK_NAME category) $(TABLE_PK_TYPE category) NOT NULL;"
	echo

	echo "ALTER TABLE $(PREFIXED $(TABLE_NAME ${table}))"
	echo "ADD FOREIGN KEY ($(TABLE_PK_NAME category)) REFERENCES $(PREFIXED $(TABLE_NAME category));"
	echo

	echo "INSERT INTO $(PREFIXED meta_relationship_column)"
	echo "(parent_catalog,parent_schema,parent_table,parent_relation,parent_column"
	echo ", child_catalog, child_schema, child_table, child_relation, child_column"
	echo ", relationship_name, ordinal_position) VALUES"
	echo "('$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME category)', 'category', '$(TABLE_PK_NAME category)'"
	echo ",'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${table})', '${table}', '$(TABLE_PK_NAME category)'"
	echo ",'category', 1);"
	echo

	if [[ "${table}" != "$(TABLE_NAME ${table})" ]]
	then
		echo "DROP VIEW $(PREFIXED ${table});"
		echo "CREATE VIEW $(PREFIXED ${table}) AS"
		echo "SELECT td.*, nd.name, nd.description"
		echo "FROM $(PREFIXED _${table}_data) td"
		echo "JOIN $(PREFIXED name_desc) nd USING($(TABLE_PK_NAME name_desc))"
		echo "WHERE nd.$(TABLE_PK_NAME locale) = $(PREFIXED get_current_locale)();"
		echo
	fi

	echo "CREATE FUNCTION $(PREFIXED trg_add_${table}_category)()"
	echo "RETURNS TRIGGER"
	echo "AS"
	echo '$$'
	echo "BEGIN"
	echo "SELECT INTO NEW.$(TABLE_PK_NAME category)"
	echo "$(PREFIXED get_next_$(TABLE_PK_NAME category))();"

	echo "INSERT INTO $(PREFIXED $(TABLE_NAME category))"
	echo "($(TABLE_PK_NAME category), $(TABLE_PK_NAME name_desc), code)"
	echo "VALUES(NEW.$(TABLE_PK_NAME category), NEW.$(TABLE_PK_NAME name_desc), ${cat_code_expr});"

	echo "RETURN NEW;"
	echo "END;"
	echo '$$'
	echo "LANGUAGE PLPGSQL;"
	echo 
	echo "CREATE TRIGGER add_${table}_category"
	echo "BEFORE INSERT OR UPDATE ON $(PREFIXED $(TABLE_NAME ${table}))"
	echo "FOR EACH ROW"
	echo "EXECUTE PROCEDURE $(PREFIXED trg_add_${table}_category)();"
	echo
	basql_set_flag TABLE_${table}_HAS_CATEGORY
}

function TABLE_HISTORY_COLNAME()
{
	basql_fetch_key_value TABLE_${1}_HISTORY_COLNAME
}

function basql_TABLE_WITH_HISTORY()
{
	colname="${2}_date"
	echo "ALTER TABLE $(PREFIXED $(TABLE_NAME ${1}))"
	echo "ADD COLUMN ${colname} $(DATE) NOT NULL DEFAULT CURRENT_DATE;"
	echo
	basql_set_flag TABLE_${1}_HAS_HISTORY
	basql_store_key_value TABLE_${1}_HISTORY_COLNAME "${colname}"
}

function basql_TABLE_WITH_SUBJECT_HISTORY()
{
	table="${1}"
	type_table="${2}"
	shift

	echo "CREATE FUNCTION gen_seq.${table}_intervals()"
	echo "RETURNS TABLE ("
	echo "	$(TABLE_PK_NAME subject) $(TABLE_PK_TYPE subject),"
	echo "	$(TABLE_PK_NAME ${type_table}) $(TABLE_PK_TYPE ${type_table}),"
	echo "	$(DURATION_BEGIN_COLNAME) $(DATE_TIME),"
	echo "	$(DURATION_END_COLNAME) $(DATE_TIME)"
	echo ")"
	echo "AS"
	echo '$$'
	echo "DECLARE"
	echo "	c_$(TABLE_PK_NAME subject) $(TABLE_PK_TYPE subject);"
	echo "	p_$(TABLE_PK_NAME subject) $(TABLE_PK_TYPE subject);"
	echo "	c_$(TABLE_PK_NAME ${type_table}) $(TABLE_PK_TYPE ${type_table});"
	echo "	p_$(TABLE_PK_NAME ${type_table}) $(TABLE_PK_TYPE ${type_table});"
	echo "	c_date $(DATE_TIME);"
	echo "	p_date $(DATE_TIME);"
	echo "BEGIN"
	echo "	p_date := NULL;"
	echo "	p_$(TABLE_PK_NAME subject) := NULL;"
	echo "	p_$(TABLE_PK_NAME ${type_table}) := NULL;"
	echo
	echo "	FOR c_$(TABLE_PK_NAME subject), c_$(TABLE_PK_NAME ${type_table}), c_date IN"
	echo "	SELECT t.$(TABLE_PK_NAME subject), t.$(TABLE_PK_NAME ${type_table}), t.$(TABLE_HISTORY_COLNAME ${table})"
	echo "	FROM $(PREFIXED ${table}) t"
	echo "	ORDER BY t.$(TABLE_PK_NAME subject), t.$(TABLE_PK_NAME ${type_table}), t.$(TABLE_HISTORY_COLNAME ${table})"
	echo "	LOOP"
	echo "		IF	(p_$(TABLE_PK_NAME subject) IS NOT NULL AND p_$(TABLE_PK_NAME subject) != c_$(TABLE_PK_NAME subject)) OR"
	echo "			(p_$(TABLE_PK_NAME ${type_table}) IS NOT NULL AND p_$(TABLE_PK_NAME ${type_table}) != c_$(TABLE_PK_NAME ${type_table}))"
	echo "		THEN RETURN QUERY"
	echo "		SELECT p_$(TABLE_PK_NAME subject), p_$(TABLE_PK_NAME ${type_table}), p_date, CAST(NULL AS $(DATE_TIME));"
	echo "		END IF;"
	echo
	echo "		RETURN QUERY"
	echo "		SELECT c_$(TABLE_PK_NAME subject), c_$(TABLE_PK_NAME ${type_table}), p_date, c_date;"
	echo
	echo "	p_date := c_date;"
	echo "	p_$(TABLE_PK_NAME subject) := c_$(TABLE_PK_NAME subject);"
	echo "	p_$(TABLE_PK_NAME ${type_table}) := c_$(TABLE_PK_NAME ${type_table});"
	echo "	END LOOP;"
	echo
	echo "	IF p_$(TABLE_PK_NAME subject) IS NOT NULL OR p_$(TABLE_PK_NAME ${type_table}) IS NOT NULL"
	echo "	THEN RETURN QUERY"
	echo "	SELECT p_$(TABLE_PK_NAME subject), p_$(TABLE_PK_NAME ${type_table}), p_date, CAST(NULL AS $(DATE_TIME));"
	echo "	END IF;"
	echo "END"
	echo '$$'
	echo "LANGUAGE PLPGSQL;"
	echo
	echo "CREATE VIEW $(PREFIXED ${table}_history)"
	echo "AS"
	echo "SELECT *"
	echo "FROM $(PREFIXED ${table})"
	echo "NATURAL JOIN $(PREFIXED ${table}_intervals)();"
	echo
}

function DURATION_BEGIN_COLNAME()
{
	echo "date_from"
}

function DURATION_END_COLNAME()
{
	echo "date_to"
}

function basql_TABLE_WITH_DURATION()
{
	echo "ALTER TABLE $(PREFIXED $(TABLE_NAME ${1}))"
	echo "ADD COLUMN $(DURATION_BEGIN_COLNAME) $(DATE) NOT NULL DEFAULT CURRENT_DATE;"
	echo "ALTER TABLE $(PREFIXED $(TABLE_NAME ${1}))"
	echo "ADD COLUMN $(DURATION_END_COLNAME) $(DATE) NULL;"
	echo
	basql_set_flag TABLE_${1}_HAS_DURATION
}

function basql_TABLE_FAKE_REF()
{
	local table="${1}"
	local dst_table="${2}"
	local pk_name="$(TABLE_PK_NAME ${dst_table})"
	local pk_type="$(TABLE_PK_TYPE ${dst_table})"
	shift 2

	echo "ALTER TABLE $(PREFIXED $(TABLE_NAME ${table}))"
	echo "ADD COLUMN ${pk_name} ${pk_type} ${@};"
	echo
	echo "INSERT INTO $(PREFIXED meta_relationship_column)"
	echo "(parent_catalog,parent_schema,parent_table,parent_relation,parent_column"
	echo ", child_catalog, child_schema, child_table, child_relation, child_column"
	echo ", relationship_name, ordinal_position) VALUES"
	echo "('$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${dst_table})', '${dst_table}', '${pk_name}'"
	echo ",'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${table})', '${table}', '${pk_name}'"
	echo ",'${dst_table}', 1);"
	echo
	basql_append_key_value TABLE_${table}_COLUMNS "${pk_name}"
	basql_append_key_value TABLE_${table}_${pk_name}_REF_TABLE "${dst_table}"
}

function basql_TABLE_REFERENCING()
{
	local table="${1}"
	local dst_table="${2}"
	local pk_name="$(TABLE_PK_NAME ${dst_table})"

	basql_TABLE_FAKE_REF "${@}"

	echo "ALTER TABLE $(PREFIXED $(TABLE_NAME ${table}))"
	echo "ADD FOREIGN KEY (${pk_name})"
	echo "REFERENCES $(PREFIXED $(TABLE_NAME ${dst_table}));"
	echo
}

function basql_TABLE_ROLE_REF() 
{
	local table="${1}"
	local dst_table="${2}"
	local pk_name="$(TABLE_PK_NAME ${dst_table})"
	local pk_type="$(TABLE_PK_TYPE ${dst_table})"
	local pk_kind="$(TABLE_PK_KIND ${dst_table})"
	local rolename="${3}_${pk_kind}"
	local relshipname="${3}"
	shift 3

	echo "ALTER TABLE $(PREFIXED $(TABLE_NAME ${table}))"
	echo "ADD COLUMN ${rolename} ${pk_type} ${@};"
	echo
	echo "ALTER TABLE $(PREFIXED $(TABLE_NAME ${table}))"
	echo "ADD FOREIGN KEY (${rolename})"
	echo "REFERENCES $(PREFIXED $(TABLE_NAME ${dst_table}));"
	echo
	echo "INSERT INTO $(PREFIXED meta_relationship_column)"
	echo "(parent_catalog,parent_schema,parent_table,parent_relation,parent_column"
	echo ", child_catalog, child_schema, child_table, child_relation, child_column"
	echo ", relationship_name, ordinal_position) VALUES"
	echo "('$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${dst_table})', '${dst_table}', '${pk_name}'"
	echo ",'$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${table})', '${table}', '${rolename}'"
	echo ",'${relshipname}', 1);"
	echo
	basql_append_key_value TABLE_${table}_COLUMNS "${rolename}"
	basql_append_key_value TABLE_${table}_${rolename}_REF_TABLE "${dst_table}"
	basql_append_key_value TABLE_${table}_${rolename}_REF_COLUMN "${pk_name}"
}

function basql_TABLE_STR_REF()
{
	local table="${1}"
	local dst_table="${2}"
	local str_code="${3}"
	shift 3

	if basql_is_flag_set TABLE_${dst_table}_HAS_STR_CODE
	then
		local pk_name="$(TABLE_PK_NAME ${dst_table})"
		local fk_name="$(TABLE_PK_NAME ${dst_table})"
		local pk_type="$(TABLE_COLUMN_TYPE ${dst_table} str_code $(STR_CODE))"
		local fn_name="sync_${table}_${dst_table}_fk_str_code"

		echo "ALTER TABLE $(PREFIXED $(TABLE_NAME ${table}))"
		echo "ADD COLUMN ${str_code} ${pk_type} ${@};"
		echo

		echo "CREATE FUNCTION $(PREFIXED ${fn_name})()"
		echo "RETURNS TRIGGER AS"
		echo '$$'
		echo "DECLARE"
		echo "OLD_${fk_name} $(PREFIXED ${table}.${fk_name}%TYPE);"
		echo "OLD_${str_code} $(PREFIXED ${table}.${str_code}%TYPE);"
		echo "BEGIN"
		echo "IF TG_OP = 'UPDATE'"
		echo "THEN"
		echo "	OLD_${fk_name} := OLD.${fk_name};"
		echo "	OLD_${str_code} := OLD.${str_code};"
		echo "ELSE"
		echo "	OLD_${fk_name} := NULL;"
		echo "	OLD_${str_code} := NULL;"
		echo "END IF;"
		echo "IF NEW.${str_code} IS NOT NULL AND coalesce(NEW.${str_code} != OLD_${str_code}, TRUE)"
		echo "THEN SELECT $(SCHEMA_NAME).get_${dst_table}(NEW.${str_code}) INTO NEW.${fk_name};"
		echo "ELSIF NEW.${fk_name} IS NOT NULL AND coalesce(NEW.${fk_name} != OLD_${fk_name}, TRUE)"
		echo "THEN SELECT str_code INTO NEW.${str_code} FROM $(PREFIXED ${dst_table}) WHERE ${pk_name} = NEW.${fk_name};"
		echo "END IF;"
		echo "RETURN NEW;"
		echo "END;"
		echo '$$'
		echo "LANGUAGE PLPGSQL;"
		echo
		echo "CREATE TRIGGER ${fn_name}"
		echo "BEFORE INSERT OR UPDATE"
		echo "ON $(PREFIXED ${table})"
		echo "FOR EACH ROW"
		echo "EXECUTE PROCEDURE $(PREFIXED ${fn_name})();"
		echo


		basql_append_key_value TABLE_${table}_COLUMNS "${str_code}"

	else basql_error "'${table}' STR_REF target table '${dst_table}' does not have str_code"
	fi

}

function basql_TABLE_WITH_REFERENCE_TO()
{
	basql_TABLE_REFERENCING "${1}" "${2}" NOT NULL
}

function basql_TABLE_WITH_WEAK_REF_TO()
{
	basql_TABLE_REFERENCING "${1}" "${2}" NULL
}

function basql_TABLE_WITH_FAKE_REF_TO()
{
	basql_TABLE_FAKE_REF "${1}" "${2}" NOT NULL
}

function basql_TABLE_WITH_ENUM_REF_TO()
{
	table="${1}"
	dst_table="${2}"
	shift 2
	basql_TABLE_FAKE_REF "${table}" "${dst_table}" NOT NULL CHECK "($(TABLE_PK_NAME ${dst_table}) IN (${@}))"
}

function basql_TABLE_WITH_ROLE_REF_TO()
{
	basql_TABLE_ROLE_REF "${1}" "${2}" "${3}" NOT NULL
}

function basql_TABLE_WITH_WEAK_ROLE_REF_TO()
{
	basql_TABLE_ROLE_REF "${1}" "${2}" "${3}" NULL
}

function basql_TABLE_WITH_STR_REF_TO()
{
	basql_TABLE_FAKE_REF "${1}" "${2}" NULL
	basql_TABLE_STR_REF  "${1}" "${2}" "${2}_str_code" NOT NULL
}

function basql_TABLE_WITH_WEAK_STR_REF_TO()
{
	basql_TABLE_FAKE_REF "${1}" "${2}" NULL
	basql_TABLE_STR_REF  "${1}" "${2}" "${2}_str_code" NULL
}

function basql_TABLE_WITH_REMOVED_DUPLICITIES()
{
	relation=${1}

	echo "--"
	echo "-- REMOVE_DUPLICITIES ${relation}"
	echo "--"
	echo "CREATE TABLE $(PREFIXED _dup_${relation}) AS"
	echo "SELECT * FROM $(PREFIXED ${relation});"
	echo
	echo "CREATE OR REPLACE FUNCTION $(PREFIXED _remove_${relation}_dups)()"
	echo "RETURNS TRIGGER"
	echo "AS"
	echo '$$'
	echo "BEGIN"
	echo "	INSERT INTO $(PREFIXED ${relation}) (SELECT NEW.*);"
	echo "	RETURN NULL;"
	echo "EXCEPTION WHEN unique_violation"
	echo "THEN RETURN NULL;"
	echo "END;"
	echo '$$'
	echo "LANGUAGE PLPGSQL;"
	echo
	echo "CREATE TRIGGER remove_dups"
	echo "BEFORE INSERT ON $(PREFIXED _dup_${relation})"
	echo "FOR EACH ROW"
	echo "EXECUTE PROCEDURE $(PREFIXED _remove_${relation}_dups)();"
}

function basql_CREATE_TABLE()
{
	local name="${1}"
	shift
	if basql_valid_identifier "${name}"
	then
		echo "--"
		echo "-- TABLE ${name}"
		echo "--"
		echo "CREATE TABLE $(PREFIXED ${name}) ();"
		echo
		while [[ "${1}" != "" ]]
		do
			local clause="${1}"
			shift
			case "${clause}" in
			WITH)
				local item="${1}"
				shift
				basql_TABLE_WITH_${item} "${name}" ${@}

				case "${item}" in
				HISTORY) shift;;
				REFERENCE_TO) shift;;
				WEAK_REF_TO) shift;;
				FAKE_REF_TO) shift;;
				ENUM_REF_TO) shift;;
				STR_REF_TO) shift;;
				WEAK_STR_REF_TO) shift;;
				ROLE_REF_TO) shift 2;;
				WEAK_ROLE_REF_TO) shift 2;;
				PRIMARY_KEY) shift 2;;
				STR_CODE)
					if [[ "${1}" =~ ^[0-9]+$ ]]
					then shift
					fi
					;;
				esac
				;;
			*) basql_error "Unknown clause ${clause}";;
			esac
		done
	fi
}

function basql_ALTER_TABLE()
{
	name="${1}"
	shift
	if basql_valid_identifier "${name}"
	then
		while [[ "${1}" != "" ]]
		do
			local clause="${1}"
			shift
			case "${clause}" in
			WITH)
				local item="${1}"
				shift
				case "${item}" in
				NAME_DESC);;
				REFERENCE_TO);;
				WEAK_REF_TO);;
				FAKE_REF_TO);;
				ENUM_REF_TO);;
				ROLE_REF_TO);;
				WEAK_ROLE_REF_TO);;
				STR_REF_TO);;
				SUBJECT_HISTORY);;
				CATEGORY);;
				REMOVED_DUPLICITIES);;
				*) basql_error "Cannot ALTER WITH ${item}.";;
				esac

				basql_TABLE_WITH_${item} "${name}" ${@}
				break;;
			ADD)
				echo "ALTER TABLE $(PREFIXED $(TABLE_NAME ${name}))"
				if [[ "${1}_${2}" == "PRIMARY_KEY" ]]
				then
					shift 2
					echo "ADD PRIMARY KEY (${@});"
					if [[ ${#} -eq 1 ]]
					then
						basql_store_key_value "TABLE_${name}_PK_NAME" "${1}"
						basql_erase_key_value TABLE_${name}_COLUMNS "${1}"
					fi
				elif [[ "${1}" == "COLUMN" ]]
				then
					shift
					basql_append_key_value TABLE_${name}_COLUMNS "${1}"
					echo "ADD COLUMN ${@};"
				else echo "${clause} ${@};"
				fi
				break;;
			*)
				echo "ALTER TABLE $(PREFIXED $(TABLE_NAME ${name}))"
				echo "${clause} ${@};"
				break;;
			esac
		done
		echo
	fi
}
