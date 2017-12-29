function basql_valid_identifier()
{
	if [[ "$(echo ${1} | tr -d 'A-Za-z0-9_.')" != "" ]]
	then echo "Invalid identifier '${1}'" && return 1
	fi
	return 0
}

