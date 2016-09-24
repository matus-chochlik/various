# Copyright Matus Chochlik.
# Distributed under the Boost Software License, Version 1.0.
# See accompanying file LICENSE_1_0.txt or copy at
#  http://www.boost.org/LICENSE_1_0.txt

import os
import ycm_core


def default_opts():
	qtdir = 'qt5'
	result = [
		'-pedantic',
		'-Wall',
		'-Weverything',
		'-Werror',
		'-Wno-c++98-compat',
		'-Wno-c++98-compat-pedantic',
		'-Wno-undef',
		'-Wno-global-constructors',
		'-Wno-exit-time-destructors',
		'-Wno-date-time',
		'-Wno-padded',
		'-Wno-missing-prototypes',
		'-Wno-documentation-unknown-command',
		'-std=c++11',
		'-x', 'c++',
		'-isystem', '/usr/include',
		'-isystem', '/usr/local/include',
		'-D_REENTRANT',
		'-DQT_CORE_LIB',
		'-DQT_GUI_LIB',
		'-DQT_NETWORK_LIB',
		'-DQT_QML_LIB',
		'-DQT_QUICK_LIB',
		'-DQT_SQL_LIB',
		'-DQT_WIDGETS_LIB',
		'-DQT_XML_LIB',
		'-I', '/usr/include/%s' % (qtdir)
	]
	for subdir in [
		"QtCore",
		"QtDBus",
		"QtGui",
		"QtHelp",
		"QtConcurrent",
		"QtMultimedia",
		"QtMultimediaWidgets",
		"QtNetwork",
		"QtOpenGL",
		"QtPlatformSupport",
		"QtPositioning",
		"QtScript",
		"QtScriptTools",
		"QtSql",
		"QtSvg",
		"QtTest",
		"QtUiTools",
		"QtV8",
		"QtWebKit",
		"QtWebKitWidgets",
		"QtWidgets",
		"QtXml",
		"QtXmlPatterns"
	]:
		result += ['-I', '/usr/include/%(qtdir)s/%(subdir)s' % {
		    'qtdir': qtdir,
		    'subdir': subdir
		}]

	return result


def ThisDir():
	return os.path.dirname(os.path.abspath(__file__))

def MakePathAbsolute(path, work_dir):
	if not os.path.isabs(path):
		path = os.path.normpath(os.path.join(work_dir, path))
	return path

def MakeOptionPathsAbsolute(old_opts, work_dir = ThisDir()):
	new_opts = list()
	make_next_abs = False
	path_flags = ['-isystem', '-I', '-iquote', '--sysroot=']

	for opt in old_opts:
		new_opt = opt
		if make_next_abs:
			new_opt = MakePathAbsolute(opt, work_dir)
			make_next_abs = False
		else:
			for path_flag in path_flags:
				if opt == path_flag:
					make_next_abs = True
					break
				if opt.startswith(path_flag):
					path = opt[len(path_flag):]
					new_opt = path_flag + MakePathAbsolute(path, work_dir)
					break

		new_opts += [new_opt]

	return new_opts

def FlagsForFile(filename, ** kwargs):

	final_opts = MakeOptionPathsAbsolute(default_opts())
	final_opts += ['-I', os.path.dirname(filename) ]
	final_opts += ['-I', os.path.join(
		ThisDir(),
		'_build',
		os.path.relpath(os.path.dirname(filename), ThisDir())
	) ]

	return {
		'flags': final_opts,
		'do_cache': True
	}
