function basql_CREATE_INDEX()
{
	if [[ "${1}" != "ON" ]]
	then basql_error 'Missing the ON clause after CREATE INDEX'
	else shift
	fi

	table="${1}"
	shift

	if basql_valid_identifier "${table}"
	then
		echo "CREATE INDEX ON $(PREFIXED $(TABLE_NAME ${table})) ${@};"
		echo
	else basql_error "Invalid identifier '${table}'"
	fi
}
