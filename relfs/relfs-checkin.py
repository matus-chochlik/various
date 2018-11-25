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
    arg_setup.with_file_paths = True
    arg_setup.with_tag_labels = True

    parser = relfs.make_argument_parser(
        'relfs-checkin', 'checks-in files into a  relfs repository',
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

            for file_path in options.file_paths:
                repo_file = open_repo.checkin_file(file_path)
                repo_file.add_tags(options.tag_labels)
        except relfs.RelFsError as relfs_error:
            relfs.print_error(relfs_error)
#------------------------------------------------------------------------------#
