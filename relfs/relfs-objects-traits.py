#!/usr/bin/env python
# coding=utf-8
#------------------------------------------------------------------------------#
import os
import sys
import json
import relfs
import logging
import fileinput
#------------------------------------------------------------------------------#
def make_arg_parser():
    arg_setup = relfs.ArgumentSetup()
    arg_setup.with_repo_names = True
    arg_setup.existing_repos = True

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


    sys.stdout.write("[")
    try:
        repos = {n: relfs.read_repository(n) for n in options.repositories}
        first = True

        for line in fileinput.input():
            split_line = line.strip().split(":")
            if len(split_line) > 1:
                repo_names = split_line[0:1]
                obj_hash = split_line[1]
            else:
                repo_names = options.repositories
                obj_hash = split_line[0]

            for repo_name in repo_names:
                try:
                    repo = repos[repo_name]
                except KeyError:
                    repo = relfs.open_repository(repo_name)
                    repos[repo_name] = repo

                valid_hash = repo.valid_object_hash(obj_hash)
                if valid_hash:
                    entity  = repo.context().find_object(valid_hash)

                    cmps = {}
                    for cmp_name, component in entity.all_components():
                        cmps[cmp_name] = component.public_values()

                    traits = {
                        "repo": repo_name,
                        "obj": valid_hash,
                        "name": entity .display_name(),
                        "exts": entity .extensions(),
                        "cmps": cmps
                    }


                    if first: first = False
                    else: sys.stdout.write("\n,")
                    sys.stdout.write(json.dumps(traits))

    except relfs.RelFsError as relfs_error:
        relfs.print_error(relfs_error)
    sys.stdout.write("]\n")
#------------------------------------------------------------------------------#
