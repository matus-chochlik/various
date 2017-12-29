function basql_IMPORT_GENE_DATA_sed()
{
organism="${1}"
echo "\
s/'/''/g;\
s/^\([^	]*\)	\([^	]*\)/\
INSERT INTO $(PREFIXED $(TABLE_NAME name_desc))\
($(TABLE_PK_NAME name_desc), $(TABLE_PK_NAME locale), name, description)\n\
VALUES($(PREFIXED get_next_$(TABLE_PK_NAME name_desc))(), 'en_US', '\1', '\2')\;\n\
INSERT INTO $(PREFIXED $(TABLE_NAME gene))\
($(TABLE_PK_NAME gene), str_code, $(TABLE_PK_NAME name_desc))\n\
VALUES($(PREFIXED get_next_$(TABLE_PK_NAME gene))(), '\1', $(PREFIXED get_last_$(TABLE_PK_NAME name_desc))())\;\n\
/p"
}

function basql_IMPORT_GENE_DATA()
{
	for txt
	do
		echo "--"
		echo "-- IMPORT ${txt}"
		echo "--"

		kind="$(basename ${txt} .txt)"
		kind="${kind#gene_}"

		sed -n "$(basql_IMPORT_GENE_DATA_sed ${kind})" < ${IMPORT_WD}${txt}

	done
}

function IMPORT()
{
	item="${1}"
	shift

	case "${item}" in
	VERBATIM)
		name="${1}"
		shift
		cat ${IMPORT_WD}${basql_export_mode}/${name}.sql ||\
		basql_error "Could not import native SQL"
		;;
	FUNCTION)
		name="${1}"
		ovld="${2}"
		shift 2
		echo -n "CREATE OR REPLACE FUNCTION $(PREFIXED ${name}) "
		cat ${IMPORT_WD}${basql_export_mode}/${name}${ovld:+-}${ovld}.sqlf ||\
		basql_error "Could not find function definition"
		echo ";"
		;;
	GENE_DATA)
		basql_IMPORT_GENE_DATA "${@}"
		;;
	*) basql_error "Invalid import item '${item}'";;
	esac
}
