# coding=utf-8
# Copyright Matus Chochlik.
# Distributed under the Boost Software License, Version 1.0.
# See accompanying file LICENSE_1_0.txt or copy at
#  http://www.boost.org/LICENSE_1_0.txt
#
import os, sys 

def print_bash_complete_script(argparser, function_name, command_name):

	import argparse

	print('#  Distributed under the Boost Software License, Version 1.0.')
	print('#  (See accompanying file LICENSE_1_0.txt or copy at')
	print('#  http://www.boost.org/LICENSE_1_0.txt)')
	print('#')
	print('#  Automatically generated file. Do NOT modify manually,')
	print('#  edit %(self)s instead' % {"self" : os.path.basename(sys.argv[0])})
	print(str())
	print('function %(function_name)s()' % {
		"function_name": function_name
	})
	print('{')
	print('	COMPREPLY=()')
	print('	local curr="${COMP_WORDS[COMP_CWORD]}"')
	print('	local prev="${COMP_WORDS[COMP_CWORD-1]}"')
	print(str())

	options_with_path=list()
	for action in argparser._actions:
		if action.type == os.path.abspath:
			options_with_path += action.option_strings

	print('	case "${prev}" in')
	print('		-h|--help)')
	print('			return 0;;')
	print('		%s)' % str("|").join(options_with_path))
	print('			COMPREPLY=($(compgen -f "${curr}"))')
	print('			return 0;;')


	for action in argparser._actions:
		if action.choices is not None:
			print('		%s)' % str("|").join(action.option_strings))
			ch = str(" ").join([str(c) for c in action.choices])
			print('			COMPREPLY=($(compgen -W "%s" -- "${curr}"))' % ch)
			print('			return 0;;')

	print('		*)')
	print('	esac')
	print(str())

	print('	local only_once_opts=" \\')
	for action in argparser._actions:
		if type(action) != argparse._AppendAction:
			print('		%s \\' % str(" ").join(action.option_strings))
	print('	"')
	print(str())

	meog_list = list()
	meog_id = 0
	for group in argparser._mutually_exclusive_groups:
		print('	local meog_%d=" \\' % meog_id)
		for action in group._group_actions:
			print('		%s \\' % str(" ").join(action.option_strings))
		print('	"')
		print(str())
		meog_list.append('meog_%d' % meog_id)
		meog_id += 1

	print('	local repeated_opts=" \\')
	for action in argparser._actions:
		if type(action) == argparse._AppendAction:
			print('		%s \\' % str(" ").join(action.option_strings))
	print('	"')
	print(str())
	print('	local opts="${repeated_opts}"')
	print(str())
	print('	for opt in ${only_once_opts}')
	print('	do')
	print('		local opt_used=false')
	print('		for pre in ${COMP_WORDS[@]}')
	print('		do')
	print('			if [ "${opt}" == "${pre}" ]')
	print('			then opt_used=true && break')
	print('			fi')
	print('		done')
	print('		if [ "${opt_used}" == "false" ]')
	print('		then')
	print('			for meog in "${%s}"' % str('}" "${').join(meog_list))
	print('			do')
	print('				local is_meo=false')
	print('				for meo in ${meog}')
	print('				do')
	print('					if [ "${opt}" == "${meo}" ]')
	print('					then is_meo=true && break')
	print('					fi')
	print('				done')
	print('				if [ "${is_meo}" == "true" ]')
	print('				then')
	print('					for pre in ${COMP_WORDS[@]}')
	print('					do')
	print('						for meo in ${meog}')
	print('						do')
	print('							if [ "${pre}" == "${meo}" ]')
	print('							then opt_used=true && break')
	print('							fi')
	print('						done')
	print('					done')
	print('				fi')
	print('			done')
	print(str())
	print('			if [ "${opt_used}" == "false" ]')
	print('			then opts="${opts} ${opt}"')
	print('			fi')
	print('		fi')
	print('	done')
	print(str())
	print('	if [ ${COMP_CWORD} -le 1 ]')
	print('	then opts="--help ${opts}"')
	print('	fi')
	print(str())
	print('	COMPREPLY=($(compgen -W "${opts}" -- "${curr}"))')
	print('}')
	print('complete -F %(function_name)s %(command_name)s' % {
		"function_name": function_name,
		"command_name": command_name
	})

