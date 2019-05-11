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
    arg_setup.with_shared_components = True

    parser = relfs.make_argument_parser(
        os.path.basename(__file__),
        'lists shared components for each relfs repository',
        arg_setup
    )
    return parser
#------------------------------------------------------------------------------#
if __name__ == "__main__":
    logging.basicConfig()
    argparser = make_arg_parser()
    options = argparser.parse_args()

    i1 = "  " if len(options.repositories) > 1 else ""
    i2 = "  " if len(options.shared_component_names) > 1 else ""

    for repo_name in options.repositories:
        try:
            if i1: print("repository: %s" % (repo_name,))
            repository = relfs.open_repository(repo_name)
            context = repository.context()
            names = options.shared_component_names
            for name, component in context.only_components(names):
                if i2: print("%scomponent: %s" % (i1,name))
                for item in component.items():
                    print("%s%s%s" % (i1, i2, str(item)))
        except relfs.RelFsError as relfs_error:
            relfs.print_error(relfs_error)
#------------------------------------------------------------------------------#
