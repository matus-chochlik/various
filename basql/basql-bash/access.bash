function basql_GRANT()
{
	action=${1}
	shift

	case "${action}" in
		SELECT|INSERT|UPDATE|DELETE);;
		*) basql_error "Invalid action '${action}' for GRANT" && exit 1;;
	esac

	if [ "${1}" != "ON" ]
	then basql_error "Syntax error ${@}" && exit 2
	else shift
	fi
	table=${1}
	shift

	if [ "$(TABLE_NAME ${table})" != "" ] && [ "$(TABLE_NAME ${table})" != "${table}" ]
	then
		if [ "${action}" == "SELECT" ]
		then echo "GRANT ${action} ON $(PREFIXED ${table}) ${@}" ";"
		fi
		echo "GRANT ${action} ON $(PREFIXED $(TABLE_NAME ${table})) ${@}" ";"
		
	else echo "GRANT ${action} ON $(PREFIXED ${table}) ${@}" ";"
	fi

	while [[ "${1}" != "" ]]
	do
		if [[ "${1}" == "TO" ]]
		then role="${2}" && break
		fi
		shift
	done

	if [[ "${role}" != "" ]]
	then
		echo "INSERT INTO $(PREFIXED meta_relation_privilege)"
		echo "(catalog_name, schema_name, table_name, relation_name, operation_name, user_role_name)"
		echo "VALUES('$(DB_NAME)', '$(SCHEMA_NAME)', '$(TABLE_NAME ${table})', '${table}', '${action}', '${role}');"
		echo
	fi
}

function LOGIN_ROLE()
{
	echo "${DB_NAME}_login"
}

function GUEST_ROLE()
{
	echo "${DB_NAME}_guest"
}

function BROWSER_ROLE()
{
	echo "${DB_NAME}_browser"
}

function EDITOR_ROLE()
{
	echo "${DB_NAME}_editor"
}

function ADMIN_ROLE()
{
	echo "${DB_NAME}_admin"
}
