#!/usr/bin/env python
# coding=utf-8
#------------------------------------------------------------------------------#
import os
import relfs
#
from relfs.components.tags import add_tags
from relfs.components.mime import add_file_mime_type
from relfs.components.date_time import add_date_time
#------------------------------------------------------------------------------#
def make_arg_parser():
    arg_setup = relfs.ArgumentSetup()
    arg_setup.with_repo_names = True
    arg_setup.existing_repos = True
    arg_setup.at_least_one_repo = True
    arg_setup.with_file_paths = True
    arg_setup.with_tag_labels = True

    parser = relfs.make_argument_parser(
        os.path.basename(__file__),
        'checks-in files into a relfs repository',
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
            ctxt = open_repo.context()

            for file_path in options.file_paths:
                # check-in a new file
                new_obj = open_repo.checkin_file(file_path)
                # basic info
                add_file_mime_type(ctxt, new_obj, file_path)
                add_tags(ctxt, new_obj, options.tag_labels)
                # file metadata
                attribs = relfs.metadata.get_file_metadata(file_path)
                add_date_time(
                    ctxt,
                    new_obj,
                    relfs.metadata.get_file_metadata_date_time(attribs))

            # commit all changes
            open_repo.commit()
        except relfs.RelFsError as relfs_error:
            relfs.print_error(relfs_error)
#------------------------------------------------------------------------------#
