function basql_error()
{
	echo "ERROR: ${1}" 1>&2 && exit ${2:-1}
}

function basql_check_temp_dir()
{
	if [[ ! -d ${basql_temp_dir} ]]
	then basql_error "Temporary directory ${1} does not exist!" 1
	fi
	if [[ ! -w ${basql_temp_dir} ]]
	then basql_error "Temporary directory ${1} not writable!" 2
	fi
}

function basql_make_temp_dir()
{
	basql_temp_dir=/tmp/basql
	mkdir -p ${basql_temp_dir}
	basql_check_temp_dir
	rm -rf ${basql_temp_dir}/*
}

function basql_rm_temp_dir()
{
	rm -rf ${basql_temp_dir}
}

function basql_store_key_value()
{
	basql_check_temp_dir
	echo "${2}" > ${basql_temp_dir}/${1}
}

function basql_append_key_value()
{
	basql_check_temp_dir
	echo "${2}" >> ${basql_temp_dir}/${1}
}

function basql_erase_key_value()
{
	basql_check_temp_dir
	grep -v -e "^${2}\$" < ${basql_temp_dir}/${1} > ${basql_temp_dir}/${1}.tmp
	mv ${basql_temp_dir}/${1}.tmp ${basql_temp_dir}/${1}
}

function basql_fetch_key_value()
{
	basql_check_temp_dir
	if [[ -f ${basql_temp_dir}/${1} ]]
	then cat ${basql_temp_dir}/${1}
	else echo ${2}
	fi
}

function basql_set_flag()
{
	basql_store_key_value "${1}" "true"
}

function basql_is_flag_set()
{
	if [ "$(basql_fetch_key_value ${1} 'false')" == "true" ]
	then return 0
	else return 1
	fi
}

function basql_echo_sql()
{
	for token
	do
		case "${token}" in
		SELECT|UNION|FROM|JOIN|NATURAL|LEFT|RIGHT) echo;;
		*) echo -n ' ';;
		esac
		echo -n "${token}"
	done
	echo ';'
}

