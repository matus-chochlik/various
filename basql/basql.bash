#!/bin/bash
basql_export_mode="postgres"

source $(dirname $0)/basql-bash/utils.bash
source $(dirname $0)/basql-bash/include.bash
source $(dirname $0)/basql-bash/import.bash

source $(dirname $0)/basql-bash/identifier.bash
source $(dirname $0)/basql-bash/db.bash
source $(dirname $0)/basql-bash/types.bash

source $(dirname $0)/basql-bash/schema.bash
source $(dirname $0)/basql-bash/access.bash
source $(dirname $0)/basql-bash/table.bash
source $(dirname $0)/basql-bash/view.bash
source $(dirname $0)/basql-bash/function.bash
source $(dirname $0)/basql-bash/index.bash

source $(dirname $0)/basql-bash/dml.bash

source $(dirname $0)/basql-bash/dispatch.bash

source $(dirname $0)/basql-bash/finalize.bash

basql_make_temp_dir

trap basql_rm_temp_dir EXIT

while true
do
	case "${1}" in
	-o|--output)
		shift
		exec > "${1}"
		;;
	-)
		echo "Unknown argument '${1}'" 1>&2
		exit 1
		;;
	*) break;;
	esac
	shift
done

for input
do INCLUDE "${input}"
done
