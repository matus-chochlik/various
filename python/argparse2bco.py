# coding=utf-8
# Copyright Matus Chochlik.
# Distributed under the Boost Software License, Version 1.0.
# See accompanying file LICENSE_1_0.txt or copy at
#  http://www.boost.org/LICENSE_1_0.txt
#
import os, sys 

def print_line(output, linestr):
	output.write(linestr)
	output.write(os.linesep)

def print_bash_complete_script(
	argparser,
	function_name,
	command_name,
	output=sys.stdout
):

	import argparse

	print_line(output, '#  Distributed under the Boost Software License, Version 1.0.')
	print_line(output, '#  (See accompanying file LICENSE_1_0.txt or copy at')
	print_line(output, '#  http://www.boost.org/LICENSE_1_0.txt)')
	print_line(output, '#')
	print_line(output, '#  Automatically generated file. Do NOT modify manually,')
	print_line(output, '#  edit %(self)s instead' % {"self" : os.path.basename(sys.argv[0])})
	print_line(output, str())
	print_line(output, 'function %(function_name)s()' % {
		"function_name": function_name
	})
	print_line(output, '{')
	print_line(output, '	COMPREPLY=()')
	print_line(output, '	local curr="${COMP_WORDS[COMP_CWORD]}"')
	print_line(output, '	local prev="${COMP_WORDS[COMP_CWORD-1]}"')
	print_line(output, str())

	options_with_path=list()
	for action in argparser._actions:
		if action.type == os.path.abspath:
			options_with_path += action.option_strings

	print_line(output, '	case "${prev}" in')
	print_line(output, '		-h|--help)')
	print_line(output, '			return 0;;')
	print_line(output, '		%s)' % str("|").join(options_with_path))
	print_line(output, '			COMPREPLY=($(compgen -f "${curr}"))')
	print_line(output, '			return 0;;')


	for action in argparser._actions:
		if action.choices is not None:
			print_line(output, '		%s)' % str("|").join(action.option_strings))
			ch = str(" ").join([str(c) for c in action.choices])
			print_line(output, '			COMPREPLY=($(compgen -W "%s" -- "${curr}"))' % ch)
			print_line(output, '			return 0;;')

	print_line(output, '		*)')
	print_line(output, '	esac')
	print_line(output, str())

	print_line(output, '	local only_once_opts=" \\')
	for action in argparser._actions:
		if type(action) != argparse._AppendAction:
			print_line(output, '		%s \\' % str(" ").join(action.option_strings))
	print_line(output, '	"')
	print_line(output, str())

	meog_list = list()
	meog_id = 0
	for group in argparser._mutually_exclusive_groups:
		print_line(output, '	local meog_%d=" \\' % meog_id)
		for action in group._group_actions:
			print_line(output, '		%s \\' % str(" ").join(action.option_strings))
		print_line(output, '	"')
		print_line(output, str())
		meog_list.append('meog_%d' % meog_id)
		meog_id += 1

	print_line(output, '	local repeated_opts=" \\')
	for action in argparser._actions:
		if type(action) == argparse._AppendAction:
			print_line(output, '		%s \\' % str(" ").join(action.option_strings))
	print_line(output, '	"')
	print_line(output, str())
	print_line(output, '	local opts="${repeated_opts}"')
	print_line(output, str())
	print_line(output, '	for opt in ${only_once_opts}')
	print_line(output, '	do')
	print_line(output, '		local opt_used=false')
	print_line(output, '		for pre in ${COMP_WORDS[@]}')
	print_line(output, '		do')
	print_line(output, '			if [ "${opt}" == "${pre}" ]')
	print_line(output, '			then opt_used=true && break')
	print_line(output, '			fi')
	print_line(output, '		done')
	print_line(output, '		if [ "${opt_used}" == "false" ]')
	print_line(output, '		then')
	print_line(output, '			for meog in "${%s}"' % str('}" "${').join(meog_list))
	print_line(output, '			do')
	print_line(output, '				local is_meo=false')
	print_line(output, '				for meo in ${meog}')
	print_line(output, '				do')
	print_line(output, '					if [ "${opt}" == "${meo}" ]')
	print_line(output, '					then is_meo=true && break')
	print_line(output, '					fi')
	print_line(output, '				done')
	print_line(output, '				if [ "${is_meo}" == "true" ]')
	print_line(output, '				then')
	print_line(output, '					for pre in ${COMP_WORDS[@]}')
	print_line(output, '					do')
	print_line(output, '						for meo in ${meog}')
	print_line(output, '						do')
	print_line(output, '							if [ "${pre}" == "${meo}" ]')
	print_line(output, '							then opt_used=true && break')
	print_line(output, '							fi')
	print_line(output, '						done')
	print_line(output, '					done')
	print_line(output, '				fi')
	print_line(output, '			done')
	print_line(output, str())
	print_line(output, '			if [ "${opt_used}" == "false" ]')
	print_line(output, '			then opts="${opts} ${opt}"')
	print_line(output, '			fi')
	print_line(output, '		fi')
	print_line(output, '	done')
	print_line(output, str())
	print_line(output, '	if [ ${COMP_CWORD} -le 1 ]')
	print_line(output, '	then opts="--help ${opts}"')
	print_line(output, '	fi')
	print_line(output, str())
	print_line(output, '	COMPREPLY=($(compgen -W "${opts}" -- "${curr}"))')
	print_line(output, '}')
	print_line(output, 'complete -F %(function_name)s %(command_name)s' % {
		"function_name": function_name,
		"command_name": command_name
	})

