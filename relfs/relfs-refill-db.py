#!/usr/bin/env python
# coding=utf-8
#------------------------------------------------------------------------------#
import os
import relfs
#------------------------------------------------------------------------------#
def make_arg_parser():
    arg_setup = relfs.ArgumentSetup()
    arg_setup.with_repo_names = True
    arg_setup.existing_repos = True
    arg_setup.at_least_one_repo = True

    parser = relfs.make_argument_parser(
        os.path.basename(__file__),
        'rescans all repository objects fills database with metadata',
        arg_setup
    )
    return parser
#------------------------------------------------------------------------------#
if __name__ == "__main__":
    argparser = make_arg_parser()
    options = argparser.parse_args()

    for repo_name in options.repositories:
        try:
            open_repo = relfs.open_repository(repo_name)
            open_repo.refill_database()
        except relfs.RelFsError as relfs_error:
            relfs.print_error(relfs_error)
#------------------------------------------------------------------------------#
