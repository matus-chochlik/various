function basql_CREATE_VIEW()
{
	local name="${1}"
	shift
	if basql_valid_identifier "${name}"
	then
		echo "--"
		echo "-- VIEW ${name}"
		echo "--"
		echo "CREATE VIEW $(PREFIXED ${name})"
		basql_echo_sql "${@}"
		echo

		echo "INSERT INTO $(PREFIXED meta_usage)"
		echo "(used_catalog, used_schema, used_relation,"
		echo " catalog_name, schema_name, relation_name)"
		echo "SELECT"
		echo "	table_catalog, table_schema, table_name,"
		echo "	view_catalog, view_schema, view_name"
		echo "FROM information_schema.view_table_usage"
		echo "WHERE view_catalog='$(DB_NAME)'"
		echo "AND view_schema='$(SCHEMA_NAME)'"
		echo "AND view_name='${name}';"
		echo
	fi
}

