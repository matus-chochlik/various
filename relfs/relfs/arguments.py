# coding=utf-8
#------------------------------------------------------------------------------#
import os
import re
import sys
import imp
import argparse
#------------------------------------------------------------------------------#
from .core import _version_numbers
from .config import config_types, load_mount_source_config, _existing_repo_names
from .components import shared_component_names
#------------------------------------------------------------------------------#
class ArgumentSetup:
    #--------------------------------------------------------------------------#
    def __init__(self):
        self.with_repo_names = False
        self.with_repo_paths = False
        self.with_tag_labels = False
        self.with_file_paths = False
        self.with_obj_hashes = False

        self.existing_repos = False
        self.at_least_one_repo = self.with_repo_names

        self.with_config_type = False
        self.with_repo_options = False

        self.with_mount_source = False
        self.with_mount_point = False

        self.with_shared_components = False

        self.with_print_repo_name = False

#------------------------------------------------------------------------------#
class __RelfsArgumentParser(argparse.ArgumentParser):
    #--------------------------------------------------------------------------#
    def _port_number_value(self, arg):
        msg_fmt = "'%s' is not a valid port number"
        try:
            port_num = int(arg)
        except:
            raise argparse.ArgumentTypeError(msg_fmt % str(arg))

        if port_num <= 0 or port_num >= 2**16:
            raise argparse.ArgumentTypeError(msg_fmt % str(arg))

        return port_num
    #--------------------------------------------------------------------------#
    def _identifier_value(self, arg, name):
        msg_fmt = "'%s' is not a valid " + name + " identifier"
        ident = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)
        if ident.match(arg) is None:
            self.error(msg_fmt % arg)

        return arg
    #--------------------------------------------------------------------------#
    def _repo_name_value(self, arg):
        return self._identifier_value(arg, 'repository')
    #--------------------------------------------------------------------------#
    def _tag_name_value(self, arg):
        return self._identifier_value(arg, 'tag')
    #--------------------------------------------------------------------------#
    def _obj_hash_value(self, arg):
        msg_fmt = "'%s' is not a valid hash value"
        ident = re.compile(r"^[0-9A-Fa-f]{6}[0-9A-Fa-f]*\Z", re.UNICODE)
        if ident.match(arg) is None:
            self.error(msg_fmt % arg)

        return arg
    #--------------------------------------------------------------------------#
    def _default_mount_point(self):
        return os.path.join(
            os.environ.get("HOME", os.path.expanduser("~")),
            "RelFs")
    #--------------------------------------------------------------------------#
    def _valid_mount_source(self, arg):
        if not os.path.isdir(arg):
            msg = "'%s' is not a directory path" % (arg)
            raise argparse.ArgumentTypeError(msg)
        dir_path = os.path.realpath(arg)
        if not os.path.isfile(os.path.join(dir_path, ".relfs", "config")):
            msg = "'%s' is not a relfs mountable directory" % (arg)
            raise argparse.ArgumentTypeError(msg)
        return dir_path
    #--------------------------------------------------------------------------#
    def _valid_mount_point(self, arg):
        if not os.path.isdir(arg):
            msg = "'%s' is not a directory path" % (arg)
            raise argparse.ArgumentTypeError(msg)
        dir_path = os.path.realpath(arg)
        for entry in os.listdir(dir_path):
            if entry != '.relfs':
                msg = "directory '%s' is not empty" % (arg)
                raise argparse.ArgumentTypeError(msg)
        return dir_path
    #--------------------------------------------------------------------------#
    def __init__(self, arg_setup = ArgumentSetup(), **kw):
        argparse.ArgumentParser.__init__(self, **kw)

        self.arg_setup = arg_setup

        self.add_argument(
            "--version",
            action="version",
            version="%(prog)s relfs-"+".".join([str(x) for x in _version_numbers])
        )

        self.add_argument(
            "--verbose", "-v",
            dest="verbosity",
            default=0,
            action="count"
        )
        if arg_setup.with_repo_names:
            if arg_setup.existing_repos:
                self.add_argument(
                    "--repository", "-r",
                    type=self._repo_name_value,
                    nargs=1,
                    dest="repositories",
                    choices=_existing_repo_names(),
                    default=list(),
                    action="append"
                )
            elif arg_setup.with_repo_paths:
                self.add_argument(
                    "--repository", "-r",
                    nargs=2,
                    dest="repositories",
                    metavar=('REPO-NAME', 'REPO-PATH'),
                    default=list(),
                    action="append"
                )
            else:
                self.add_argument(
                    "--repository", "-r",
                    type=self._repo_name_value,
                    nargs=1,
                    dest="repositories",
                    metavar='REPO-NAME',
                    default=list(),
                    action="append"
                )

        if arg_setup.with_tag_labels:
            self.add_argument(
                "--tag", "-t",
                type=self._tag_name_value,
                nargs='?',
                dest="tag_labels",
                metavar='TAG-LABEL',
                default=list(),
                action="append"
            )

        if arg_setup.with_obj_hashes:
            self.add_argument(
                "--obj", "-o",
                type=self._obj_hash_value,
                nargs='?',
                dest="obj_hashes",
                metavar='OBJ-HASH',
                default=list(),
                action="append"
            )

        if arg_setup.with_file_paths:
            self.add_argument(
                "--file", "-f",
                metavar='FILE-PATH',
                nargs='?',
                dest="file_paths",
                default=list(),
                action="append"
            )

        if arg_setup.with_config_type:
            ct_group = self.add_mutually_exclusive_group()
            ct_group.add_argument(
                "--config-type", "-C",
                nargs='?',
                dest="config_type",
                choices=config_types(),
                default="user",
                action="store"
            )
            for conf_typ in config_types():
                ct_group.add_argument(
                    "--%s" % conf_typ,
                    dest="config_type",
                    action="store_const",
                    const=conf_typ
                )

        if arg_setup.with_repo_options:
            self.add_argument(
                "--compress", "-c",
                type=bool,
                metavar='BOOL',
                nargs='?',
                dest="compress",
                default=True,
                action="store"
            )

        if arg_setup.with_mount_source:
            self.add_argument(
                "-M", "--mount-source",
                dest="mount_source",
                type=self._valid_mount_source,
                default=None,
                action="store",
                help="""Specifies the relational filesystem mount-source path"""
            )

        if arg_setup.with_mount_point:
            self.add_argument(
                "-m", "--mount-point",
                dest="mount_point",
                type=self._valid_mount_point,
                default=self._default_mount_point(),
                action="store",
                help="""Specifies the relational filesystem mount-point path"""
            )

        if  arg_setup.with_repo_names or\
            arg_setup.with_tag_labels or\
            arg_setup.with_obj_hashes or\
            arg_setup.with_file_paths or\
            arg_setup.with_mount_source:
            mvar_list = list()
            help_list = list()

            if arg_setup.with_repo_names:
                if arg_setup.existing_repos:
                    mvar_list += [
                        '@'+x.encode('ascii', 'ignore')
                        for x in _existing_repo_names()
                    ]
                    help_list.append('repository name')
                elif arg_setup.with_repo_paths:
                    mvar_list.append('@repo dir-path')
                    help_list.append('repository name and repository path')
                else:
                    mvar_list.append('@repo')
                    help_list.append('repository name')

            if arg_setup.with_tag_labels:
                mvar_list.append(':tag-label')
                help_list.append('tag label')

            if arg_setup.with_obj_hashes:
                mvar_list.append('^obj-hash')
                help_list.append('obj hash')

            if arg_setup.with_file_paths:
                mvar_list.append('file-path')
                help_list.append('file path')

            self.add_argument(
                "arguments",
                metavar="|".join(mvar_list),
                nargs='*',
                type=str,
                help=" or ".join(help_list)
            )

        if arg_setup.with_shared_components:
            self.add_argument(
                "--shared-components", "-S",
                dest="shared_component_names",
                choices=shared_component_names(),
                default=[],
                action="append"
            )

        if arg_setup.with_print_repo_name:
            self.add_argument(
                "--print-repo", "-pr",
                dest="do_print_repo_name",
                default=None,
                action="store_true"
            )
            self.add_argument(
                "--dont-print-repo", "-PR",
                dest="do_print_repo_name",
                action="store_false"
            )

        try:
            imp.find_module('argparse2bco')
            self.add_argument(
                "--print-bash-complete",
                action="store_true",
                default=False
            )
        except ImportError: pass
    #--------------------------------------------------------------------------#
    def _normalize_list(self, lst):
        result = set()
        for item in lst:
            if type(item) is list:
                for subitem in self._normalize_list(item):
                    result.add(subitem)
            else:
                result.add(item)
        return list(result)

    #--------------------------------------------------------------------------#
    def process_parsed_options(self, options):
        options.arg_setup = self.arg_setup

        try:
            if options.print_bash_complete:
                self.print_bash_complete(
                    '_complete_' + re.sub('[^0-9a-zA-Z]+', '_', self.prog),
                    sys.argv[0]
                )
                self.exit()
        except AttributeError: pass

        if self.arg_setup.with_repo_paths:
            repos = list()
            for i in xrange(0, len(options.arguments)):
                try: this_arg = options.arguments[i]
                except IndexError: break

                try: next_arg = options.arguments[i+1]
                except IndexError: next_arg = ""

                if this_arg[0] == '@':
                    if not next_arg or next_arg[0] in ['@', ':', '^']:
                        self.error("a path is required after '%s'" % this_arg)
                    else:
                        repos.append([this_arg[1:], next_arg])
                        del(options.arguments[i+1])

        else:
            repos  = [x[1:] for x in options.arguments if x[0] == '@']

        tags   = [x[1:] for x in options.arguments if x[0] == ':']
        hashes = [x[1:] for x in options.arguments if x[0] == '^']
        other  = [x for x in options.arguments if x[0] not in ['@',':','^']]
        files  = [x for x in other if os.path.isfile(x)]

        if self.arg_setup.with_mount_source:
            sources = [x for x in other if self._valid_mount_source(x)]
            sources = list(dict.fromkeys(sources))
            if options.mount_source:
                if len(sources) > 0:
                    self.error("too many mount source directories specified")
            else:
                if len(sources) < 1:
                    self.error("a mount source directory is required")
                elif len(sources) > 1:
                    self.error("too many mount source directories specified")
                else:
                    options.mount_source = sources[0]

            try:
                mnt_src_config = load_mount_source_config(options)
                repos += mnt_src_config.repositories
            except Exception as bla: print(bla)

        if self.arg_setup.with_repo_names:
            options.repositories += repos

            if self.arg_setup.at_least_one_repo and\
                len(options.repositories) == 0:
                self.error("at least one repository name must be specified")

            options.repositories = self._normalize_list(options.repositories)

            if self.arg_setup.with_repo_paths:
                options.repositories = {
                    self._repo_name_value(repo): path
                    for repo, path in options.repositories
                }
            else:
                options.repositories = [
                    self._repo_name_value(repo)
                    for repo in options.repositories
                ]
        elif len(repos) > 0:
            self.error(
                "unexpected repository name '%s' in argument list" % repos[0]
            )

        if self.arg_setup.with_tag_labels:
            options.tag_labels += [self._tag_name_value(t) for t in tags]
        elif len(tags) > 0:
            self.error(
                "unexpected tag '%s' in argument list" % tags[0]
            )

        if self.arg_setup.with_file_paths:
            options.file_paths += files
        elif len(files) > 0:
            self.error(
                "unexpected file path '%s' in argument list" % files[0]
            )

        if self.arg_setup.with_obj_hashes:
            options.obj_hashes += hashes
        elif len(hashes) > 0:
            self.error(
                "unexpected object hash '%s' in argument list" % hashes[0]
            )

        if self.arg_setup.with_file_paths:
            options.file_paths = \
                [os.path.realpath(p) for p in options.file_paths]

        if self.arg_setup.with_repo_names:
            if self.arg_setup.with_repo_paths:
                options.repositories = {
                    repo_name: os.path.realpath(repo_path)
                    for repo_name, repo_path in options.repositories.items()
                }

        options.__dict__.pop("arguments", None)

        Options = options.__class__

        if self.arg_setup.with_print_repo_name:
            def __opts_print_repo_names(options, hint = None):
                if hint is None:
                    hint = len(options.repositories) > 1
                if options.do_print_repo_name is not None:
                    return options.do_print_repo_name
                else:
                    return hint

            setattr(
                options,
                "print_repo_names",
                __opts_print_repo_names.__get__(options, Options)
            )

        return options
    #--------------------------------------------------------------------------#
    #--------------------------------------------------------------------------#
    def parse_args(self):
        return self.process_parsed_options(
            argparse.ArgumentParser.parse_args(self)
        )
    #--------------------------------------------------------------------------#
    def print_bash_complete(self, function_name, command):
        import argparse2bco
        argparse2bco.print_bash_complete_script(
            self,
            function_name,
            command
        )
#------------------------------------------------------------------------------#
def make_argument_parser(command, description, arg_setup = ArgumentSetup()):
    argparser = __RelfsArgumentParser(
        arg_setup = arg_setup,
        prog=command,
        description=description,
        epilog="""
            Copyright (c) Matúš Chochlík.
            Permission is granted to copy, distribute and/or modify this document
            under the terms of the Boost Software License, Version 1.0.
            (See a copy at http://www.boost.org/LICENSE_1_0.txt)
        """
    )

    return argparser
#------------------------------------------------------------------------------#
