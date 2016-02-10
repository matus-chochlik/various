#/bin/bash
gimp -n -i -b - < $(dirname $0)/$(basename $0 .sh).txt
