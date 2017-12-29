function DB_NAME()
{
	echo "${DB_NAME}"
}

function SCHEMA_NAME()
{
	echo "${SCHEMA_NAME}"
}

function PREFIXED()
{
	echo "${SCHEMA_NAME}.${1}"
}
