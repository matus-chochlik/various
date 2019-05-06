#!/usr/bin/env python
# coding=utf-8
#------------------------------------------------------------------------------#
import os
import logging
from relfs import open_repository, RelFsError, print_error
#
from relfs.metadata import \
        get_file_metadata_date_time, \
        get_file_metadata_picture_info, \
        get_file_metadata
#
from relfs.components.tags import add_tags
from relfs.components.mime import add_file_mime_type
from relfs.components.date_time import add_date_time
from relfs.components.picture_info import add_picture_info
#------------------------------------------------------------------------------#
def make_arg_parser():
    from relfs import ArgumentSetup, make_argument_parser
    arg_setup = ArgumentSetup()
    arg_setup.with_repo_names = True
    arg_setup.existing_repos = True
    arg_setup.at_least_one_repo = True
    arg_setup.with_file_paths = True
    arg_setup.with_tag_labels = True

    parser = make_argument_parser(
        os.path.basename(__file__),
        'checks-in files into a relfs repository',
        arg_setup
    )
    return parser
#------------------------------------------------------------------------------#
if __name__ == "__main__":
    logging.basicConfig()
    argparser = make_arg_parser()
    options = argparser.parse_args()

    for repo_name in options.repositories:
        try:
            open_repo = open_repository(repo_name)
            ctxt = open_repo.context()

            for file_path in options.file_paths:
                # check-in a new file
                new_obj = open_repo.checkin_file(file_path)
                # basic info
                add_file_mime_type(ctxt, new_obj, file_path)
                add_tags(ctxt, new_obj, options.tag_labels)
                # file metadata
                attribs = get_file_metadata(file_path)
                add_date_time(
                    ctxt,
                    new_obj,
                    get_file_metadata_date_time(attribs))
                add_picture_info(
                    ctxt,
                    new_obj,
                    get_file_metadata_picture_info(attribs))

            # commit all changes
            open_repo.commit()
        except RelFsError as relfs_error:
            print_error(relfs_error)
#------------------------------------------------------------------------------#
