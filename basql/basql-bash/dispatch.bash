function CREATE()
{
	item="${1}"
	shift
	case ${item} in
	SCHEMA|DOMAIN|TABLE|VIEW|UNIQUE|INDEX|INSERTER|UPDATERS|DELETERS)
		basql_CREATE_${item} "${@}";;
	*) basql_error "Unknown object type '${item}'"
	esac
}

function CREATE_UNIQUE()
{
	item="${1}"
	shift
	case ${item} in
	INDEX)
		basql_CREATE_UNIQUE_${item} "${@}";;
	*) basql_error "Unknown object type '${item}'"
	esac
}

function ALTER()
{
	item="${1}"
	shift
	case ${item} in
	TABLE)
		basql_ALTER_${item} "${@}";;
	*) basql_error "Unknown object type '${item}'"
	esac
}

function GRANT()
{
	basql_GRANT "${@}"
}

function INSERT()
{
	item="${1}"
	shift
	case ${item} in
	INTO|LOCALE|NAME_DESC|ID_ETC|\
	COUNTRY|TYPE|GENE_SPEC|\
	META_RELATION|META_COLUMN|META_FOREIGN_COLUMN|\
	META_RELATIONSHIP_COLUMN|\
	META_FUNCTION|META_OPERATION|\
	META_GROUP|META_SCHEMA)
		basql_INSERT_${item} "${@}";;
	*) basql_error "Syntax error 'INSERT ${item}'";;
	esac
}

function SET()
{
	item="${1}"
	shift
	case ${item} in
	ID_SEQUENCE)
		basql_SET_${item} "${@}";;
	*) basql_error "Syntax error 'SET ${item}'";;
	esac
}
