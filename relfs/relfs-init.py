#!/usr/bin/env python
# coding=utf-8
#------------------------------------------------------------------------------#
import relfs
#------------------------------------------------------------------------------#
def make_arg_parser():
	arg_setup = relfs.ArgumentSetup()
	arg_setup.with_repo_names = True
	arg_setup.with_repo_paths = True
	arg_setup.existing_repos = False
	arg_setup.at_least_one_repo = True
	arg_setup.with_config_type = True

	parser = relfs.make_argument_parser(
		'relfs-init',
		'initializes a new relfs repository',
		arg_setup
	)
	return parser
#------------------------------------------------------------------------------#
if __name__ == "__main__":
	argparser = make_arg_parser()
	options = argparser.parse_args()

	for repo_name, repo_path in options.repositories.items():
		try:
			relfs.Repository.initialize(
				options.config_type,
				repo_name, repo_path,
				options
			)
		except relfs.RelFsError as relfs_error:
			relfs.print_error(relfs_error)
#------------------------------------------------------------------------------#
