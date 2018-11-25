# coding=utf-8
#------------------------------------------------------------------------------#
import os
import json
#------------------------------------------------------------------------------#
def _mkdir_p(os_path):
    try: os.makedirs(os_path)
    except OSError as os_error:
        if not(os_error.errno == os.errno.EEXIST and os.path.isdir(os_path)):
            raise
#------------------------------------------------------------------------------#
def system_config_dir_path():
    return os.path.expanduser('/etc/relfs/')
#------------------------------------------------------------------------------#
def user_config_dir_path():
    return os.path.expanduser('~/.config/relfs/')
#------------------------------------------------------------------------------#
def config_types():
    return ['system', 'user']
#------------------------------------------------------------------------------#
def config_dir_paths():
    return [system_config_dir_path(), user_config_dir_path()]
#------------------------------------------------------------------------------#
def config_dir_types_and_paths():
    return dict(zip(config_types(), config_dir_paths()))
#------------------------------------------------------------------------------#
def config_dir_path(config_type):
    return config_dir_types_and_paths()[config_type]
#------------------------------------------------------------------------------#
def __make_repo_config_file_path(config_dir):
    return os.path.join(config_dir, "repositories")
#------------------------------------------------------------------------------#
def repo_config_file_path(config_type):
    return __make_repo_config_file_path(config_dir_path(config_type))
#------------------------------------------------------------------------------#
def repo_config_file_paths():
    return [__make_repo_config_file_path(x) for x in config_dir_paths()]
#------------------------------------------------------------------------------#
def __load_config_content(file_path):
    try:
        config_file = open(file_path, 'rt')
        return json.load(config_file)
    except IOError as io_error:
        if io_error.errno == os.errno.ENOENT:
            return dict()
        else: raise
#------------------------------------------------------------------------------#
def __save_config_content(file_path, content):
    config_file = open(file_path, 'wt')
    json.dump(content, config_file, indent=2)
#------------------------------------------------------------------------------#
class __ConfigStruct(object):
    def __init__(self, entries):
        self.repositories = dict()
        self.__dict__.update(entries)
#------------------------------------------------------------------------------#
def load_all_configs():
    config = dict()
    for file_path in repo_config_file_paths():
        config.update(__load_config_content(file_path))

    return __ConfigStruct(config)
#------------------------------------------------------------------------------#
def load_config_file(file_path):
    return __ConfigStruct(__load_config_content(file_path))
#------------------------------------------------------------------------------#
def load_config(config_type):
    return load_config_file(repo_config_file_path(config_type))
#------------------------------------------------------------------------------#
def save_config_file(file_path, config):
    _mkdir_p(os.path.dirname(file_path))
    assert(isinstance(config, __ConfigStruct))
    __save_config_content(file_path, config.__dict__)
#------------------------------------------------------------------------------#
def save_config(config_type, config):
    return save_config_file(repo_config_file_path(config_type), config)
#------------------------------------------------------------------------------#
__cached_config = None
def __config():
    global __cached_config
    if __cached_config is None:
        __cached_config = load_all_configs()
    return __cached_config
#------------------------------------------------------------------------------#
def _existing_repo_names():
    return list(__config().repositories.keys())
#------------------------------------------------------------------------------#
