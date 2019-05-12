#!/usr/bin/env python
# coding=utf-8
#------------------------------------------------------------------------------#
import os
import relfs
import logging
#------------------------------------------------------------------------------#
def make_arg_parser():
    arg_setup = relfs.ArgumentSetup()
    arg_setup.with_repo_names = True
    arg_setup.existing_repos = True
    arg_setup.at_least_one_repo = True
    arg_setup.with_print_repo_name = True

    parser = relfs.make_argument_parser(
        os.path.basename(__file__),
        'lists shared components for each relfs repository',
        arg_setup
    )

    parser.add_argument(
        "--brief", "-b",
        dest="brief",
        default=False,
        action="store_true"
    )

    return parser
#------------------------------------------------------------------------------#
if __name__ == "__main__":
    logging.basicConfig()
    argparser = make_arg_parser()
    options = argparser.parse_args()

    prefix = "%(r)s:" if options.print_repo_names() else ""
    fmtstr = prefix+("%(h)s" if options.brief else "s%(h)s:%(d)s%(e)s")

    for repo_name in options.repositories:
        try:
            repository = relfs.read_repository(repo_name)
            context = repository.context()
            for obj_hash, entity in context.all_objects():
                print(fmtstr % {
                    "r": repo_name,
                    "h": obj_hash,
                    "d": entity.display_name(),
                    "e": entity.extensions()
                })
        except relfs.RelFsError as relfs_error:
            relfs.print_error(relfs_error)
#------------------------------------------------------------------------------#
