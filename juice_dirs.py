"""
Move files into folders organized by category

Usage:
    juice_dirs.py PATH
"""

import yaml
import os
import sys
from docopt import docopt
from collections import namedtuple
import configparser

CONFIG_FILE = 'datajuicer.ini'
SUMMARY_FILE = 'old_paths.yaml'

def walkPath(path_str):
    """Return list of all files in path_str and subdirectories
    
    Each item in returned list is a tuple (file_name, file_size, file_path)
    """
    walk_item = os.walk(path_str)
    file_list = []
    for root, dirs, files in walk_item:
        for file_entry in files:
            file_path = os.path.join(root, file_entry)
            file_list.append((file_entry, file_path))
    return file_list

def main():
    args = docopt(__doc__)
    path_arg = args['PATH']
    if os.path.isfile(os.path.join(path_arg, CONFIG_FILE)):
        config_path = os.path.join(path_arg, CONFIG_FILE)
    else:
        config_path = os.path.join(os.path.dirname(sys.argv[0]), CONFIG_FILE)
    print('reading oonfig file at {}'.format(config_path))
    cat_list, type_dict = loadConfig(config_path)
    print(type_dict) 
    file_list = walkPath(path_arg)
    print(len(file_list), 'files found')

    juiced_dir = os.path.join(path_arg, 'dir_juice')
    os.mkdir(juiced_dir)
    cat_path_dict = {cat: os.path.join(juiced_dir, cat) for cat in cat_list}
    cat_list_dict = {cat: [] for cat in cat_list}
    for path in cat_path_dict.values(): os.mkdir(path)
    for name, path in file_list:
        ext = name[name.rfind('.') + 1:]
        if ext in type_dict:
            f_type = type_dict[ext]
            save_path = cat_path_dict[f_type]
            save_name = findName(name, save_path)
            os.replace(path, os.path.join(save_path, save_name))
            cat_list_dict[f_type].append((save_name, path))
    for cat, path in cat_path_dict.items():
        with open(os.path.join(path, SUMMARY_FILE), 'w', newline='') as f:
            yaml.dump(cat_list_dict[cat], f)
    print(*cat_list_dict.items(), sep='\n')

def findName(name, path):
    if not os.path.exists(os.path.join(path, name)):
        return name
    dup_num = 0
    new_name = (name[:name.rfind('.')] + '_' + str(dup_num) 
            + name[name.rfind('.'):])
    while os.path.exists(os.path.join(path, new_name)):
        dup_num = dup_num + 1
        new_name = (name[:name.rfind('.')] + '_' + str(dup_num) 
                + name[name.rfind('.'):])
    return new_name

def loadConfig(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    type_dict = {}
    category_list = []
    if 'file types' in config:
        for category in config['file types']:
            category_list.append(category)
            type_list = config['file types'][category].split()
            for f_type in type_list:
                type_dict.update({f_type: category}) 
    return category_list, type_dict

if __name__ == '__main__':
    main()
