function basql_escape_special_chars()
{
	local input="${*}"

	local state=""
	for i in $(seq 0 ${#1})
	do
		local c="${input:${i}:1}"
		case "${c}" in
		"'")
			if [[ "${state:0:1}" == "a" ]]
			then state="${state:1}"
			else state="a${state:0}"
			fi
			;;
		'*'|'<'|'>')
			if [[ "${state:0:1}" != "a" ]]
			then echo -n "\\\\"
			fi
			;;
		'$')
			if [[ "${state:0:1}" != "a" ]]
			then state="d${state}"
			fi
			;;
		'(')
			if [[ "${state:0:1}" != "a" ]]
			then
				if  [[ "${state:0:1}" != "d" ]]
				then state="p${state:0}" && echo -n "\\\\"
				else state="P${state:1}"
				fi
			fi
			;;
		')')
			if [[ "${state:0:1}" != "a" ]]
			then
				if [[ "${state:0:1}" == "p" ]]
				then echo -n "\\\\"
				fi
				state="${state:1}"
			fi
			;;
		*)
			if [[ "${state:0:1}" == "d" ]]
			then state="${state:1}"
			fi
			;;
		esac
		echo -n "${c}"
	done
	echo
}

function INCLUDE()
{
	local PAR_IMPORT_WD="${IMPORT_WD}"

	echo "NOTICE: Including '${1}'" 1>&2

	cut -d'#' -f1 "${IMPORT_WD}${1%.basql}.basql" |
	while read line
	do
		if [[ "${line}" == *\; ]]
		then echo "${line}"
		else echo -n "${line} "
		fi
	done |
	sed "s|'\([^']*\)'|\"'\1'\"|g" |
	while read line 
	do basql_escape_special_chars "${line}"
	done |
	while read cmd line
	do
		IMPORT_WD="$(dirname ${PAR_IMPORT_WD}${1}})/"
		eval ${cmd} ${line}
	done
	IMPORT_WD="$(dirname ${PAR_IMPORT_WD:-.})"
	return
}
