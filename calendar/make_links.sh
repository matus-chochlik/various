#!/bin/bash
this_name="$(basename $(pwd))"

for ent in "$(dirname $(pwd))"/*
do
	src_name="$(basename ${ent})"
	suffix="${this_name##${src_name}}"
	for ext in txt png
	do
		if [[ "${suffix}" != "" ]] && [[ "${suffix}" != "${this_name}" ]] && [[ -d ${ent} ]]
		then
			for lsrc in "$(dirname $(realpath $(pwd)))/${src_name}/"{??,??${suffix}}.${ext}
			do
				if [[ -f "${lsrc}" ]]
				then
					lname="$(basename ${lsrc} .${ext})"
					ln -f -s "${lsrc}" "${lname%%${suffix}}.${ext}"
				fi
			done
		fi
	done
done
