function basql_CREATE_SCHEMA()
{
	if basql_valid_identifier "${1}"
	then
		echo "CREATE SCHEMA ${1};"
		echo
	fi
	echo "GRANT USAGE ON SCHEMA ${1} TO $(LOGIN_ROLE);"
	echo "GRANT USAGE ON SCHEMA ${1} TO $(GUEST_ROLE);"
	echo "GRANT USAGE ON SCHEMA ${1} TO $(BROWSER_ROLE);"
	echo "GRANT USAGE ON SCHEMA ${1} TO $(EDITOR_ROLE);"
	echo "GRANT USAGE ON SCHEMA ${1} TO $(ADMIN_ROLE);"
}
