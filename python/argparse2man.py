# coding=utf-8
# Copyright Matus Chochlik.
# Distributed under the Boost Software License, Version 1.0.
# See accompanying file LICENSE_1_0.txt or copy at
#  http://www.boost.org/LICENSE_1_0.txt
#
import os, sys 

def get_git_config_value(section, option):
		try:
			import gitconfig
			key = "%(section)s.%(option)s" % {
				"section": section,
				"option" : option
			}
			return gitconfig.GitConfig()[key]
		except: pass

		try:
			import git
			path = [os.path.normpath(os.path.expanduser("~/.gitconfig"))]
			return git.GitConfigParser(path, read_only=True).get_value(section, option)
		except: raise

def print_line(output, linestr):
	output.write(linestr)
	output.write(os.linesep)

def adjust_attributes(command_name, attribs):
	import datetime

	attribs["date"] = str(datetime.datetime.now().date())
	attribs["command"] = command_name
	attribs["command_uc"] = command_name.upper()

	if not "brief" in attribs:
		attribs["brief"] = command_name

	if not "heading" in attribs:
		attribs["heading"] = attribs["brief"]

	if not "description" in attribs:
		attribs["description"] = command_name


	if not "author_name" in attribs:
		try:
			attribs["author_name"] = get_git_config_value('user', 'name')
		except: pass

	if not "author_email" in attribs:
		try:
			attribs["author_email"] = get_git_config_value('user', 'email')
		except: pass

	if not "author_name" in attribs:
		try:
			import getpass
			attribs["author_name"] = getpass.getuser()
		except: pass

	if not "author_name" in attribs:
		attribs["author_name"] = "Joe Developer"

	if not "author_email" in attribs:
		attribs["author_email"] = "example@example.com"

	return attribs


def print_manual(
	argparser,
	command_name,
	attributes = dict(),
	output=sys.stdout
):
	import argparse

	attributes = adjust_attributes(command_name, attributes)

	print_line(output, '.TH %(command_uc)s 1 "%(date)s" "%(heading)s"' % attributes)
	print_line(output, '.SH "NAME"')
	print_line(output, '%(command)s \\- %(brief)s' % attributes)
	print_line(output, '.SH "SYNOPSIS"')
	print_line(output, '.B %(command)s' % attributes)
	print_line(output, '[')
	print_line(output, 'OPTIONS')
	print_line(output, ']')

	print_line(output, '.SH "DESCRIPTION"')
	print_line(output, '%(description)s' % attributes)

	print_line(output, '.SH "OPTIONS"')

	for action in argparser._actions:
		print_line(output, ".TP")
		opt_info = str()
		for opt_str in action.option_strings:
			if opt_info:
				opt_info += ", "
			opt_info += '\\fB'+opt_str+'\\fR'
			if action.type == os.path.abspath:
				opt_info += ' <\\fI'+str(action.dest).upper()+'\\fR>';
			if action.choices is not None:
				opt_info += ' {\\fB'
				opt_info += '\\fR,\\fB'.join(map(str, action.choices))
				opt_info += '\\fR}'
		print_line(output, opt_info)
		print_line(output,
			str(' ').join(action.help.split()) % {
				"prog": "\\f%(command)s\\fR" % attributes,
				"default": "\\fB"+str(action.default)+"\\fR"
			}
		)


	print_line(output, '.SH "AUTHOR"')
	print_line(output, '%(author_name)s, %(author_email)s' % attributes)

	print_line(output, '.SH "COPYRIGHT"')
	print_line(output, 'Copyright (c) %(author_name)s' % attributes)

	print_line(output, ".PP")
	print_line(output, "Permission is granted to copy, distribute and/or modify this document")
	print_line(output, "under the terms of the Boost Software License, Version 1.0.")
	print_line(output, "(See a copy at http://www.boost.org/LICENSE_1_0.txt)")

