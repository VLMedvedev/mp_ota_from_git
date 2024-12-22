#import urequests
#import uhashlib
import os
import hashlib as uhashlib
import requests as urequests

import binascii
import json
from git_config import GITHUB_TOKEN, GITHUB_BRANCH, GITHUB_TREES_API_URL, GITHUB_APP_FOLDER, RAW_URL

app_trees_url_sha = None


def pull(f_path):
  print(f'pulling {f_path} from github')
  #files = os.listdir()
  headers = {'User-Agent': 'mp_ota_from_git'}
  # ^^^ Github Requires user-agent header otherwise 403
  if GITHUB_TOKEN != "":
      headers['authorization'] = "bearer %s" % GITHUB_TOKEN
  r = urequests.get(RAW_URL+f_path, headers=headers)
  try:
    new_file = open(f_path, 'w')
    new_file.write(r.content.decode('utf-8'))
    new_file.close()
  except:
    print('decode fail try adding non-code files to .gitignore')
    try:
      new_file.close()
    except:
      print('tried to close new_file to save memory durring raw file decode')


def pull_git_tree(git_folder, recursive=False):
    headers = {'User-Agent': 'mp_ota_from_git'}
    # ^^^ Github Requires user-agent header otherwise 403
    if GITHUB_TOKEN != "":
        headers['authorization'] = "bearer %s" % GITHUB_TOKEN
    if recursive:
        giturl=f"{GITHUB_TREES_API_URL}{git_folder}?recursive=1"
    else:
        giturl=f"{GITHUB_TREES_API_URL}{git_folder}"
    payload = urequests.get(giturl, headers=headers)
    return_code = payload.status_code
    if return_code == 200:
        git_tree = json.loads(payload.content.decode('utf-8'))
        if 'tree' in git_tree:
            return git_tree
    else:
        print(f'\nGit branch and folder {git_folder} not found.\n')
        #raise Exception(f'Default branch {GITHUB_BRANCH} not found.')
        return None

def parse_git_tree(tree):
    dirs = []
    files = []
    for i in tree['tree']:
        if i['type'] == 'tree':
            dirs.append(i['path'])
        if i['type'] == 'blob':
            files.append([i['path'], i['sha'], i['mode']])
    print('dirs:', dirs)
    print('files:', files)
    return dirs, files

def get_app_tree(tree=None, app_trees_url_sha = None):
    if tree is None:
        tree = pull_git_tree(GITHUB_BRANCH, recursive=False)
    for elem in tree['tree']:
        print(elem['path'])
        if elem['type'] != 'tree':
            continue
        if elem['path'] == GITHUB_APP_FOLDER:
            app_trees_url_sha = elem['sha']
            app_tree = pull_git_tree(app_trees_url_sha, recursive=True)
            return app_tree
    return None

def is_directory(file_name):
    try:
        f = os.path.isdir(file_name) #[8]
        return f
    except:
        return False

def build_internal_tree(root_path="./"):
    internal_tree = []
    exclude_list = ["__pycache__"]
    os.chdir(root_path)
    for item in os.listdir():
        if not item in exclude_list:
            add_to_tree(item, internal_tree, root_path)
    return internal_tree

def add_to_tree(dir_item, internal_tree, root_path):
   # print(dir_item)
    curent_path = os.getcwd()
    if curent_path != root_path:
        subfile_path = curent_path + '/' + dir_item
    else:
        subfile_path = curent_path + dir_item
    #print(f'sub_path: {subfile_path}')
    if is_directory(subfile_path) and len(os.listdir(subfile_path)) >= 1:
        os.chdir(subfile_path)
        for i in os.listdir():
            add_to_tree(i, internal_tree, root_path)
        os.chdir('..')
    else:
        try:
            internal_tree.append([subfile_path,get_hash(subfile_path)])
        except OSError: # type: ignore # for removing the type error indicator :)
            print(f'{dir_item} could not be added to tree')

def update(root_path="./"):
  os.chdir(root_path)
  tree = get_app_tree()
  internal_tree = build_internal_tree()
  print(internal_tree)
  log = []
  # download and save all files
  for i in tree['tree']:
    if i['type'] == 'tree':
      try:
        os.mkdir(i['path'])
      except:
        print(f'failed to {i["path"]} dir may already exist')
    elif i['path'] not in ignore:
      try:
        os.remove(i['path'])
        log.append(f'{i["path"]} file removed from int mem')
        internal_tree = remove_item(i['path'],internal_tree)
      except:
        log.append(f'{i["path"]} del failed from int mem')
        print('failed to delete old file')
      try:
        pull(i['path'],raw + i['path'])
        log.append(i['path'] + ' updated')
      except:
        log.append(i['path'] + ' failed to pull')
  # delete files not in Github tree
  if len(internal_tree) > 0:
      print(internal_tree, ' leftover!')
      for i in internal_tree:
          os.remove(i)
          log.append(i + ' removed from int mem')
  logfile = open('ugit_log.py','w')
  logfile.write(str(log))
  logfile.close()
  time.sleep(10)

def get_hash(file_name):
    print(file_name)
    file_stats = os.stat(file_name)
    file_size = file_stats.st_size
    o_file = open(file_name, mode='r')
    r_file = o_file.read()
    #file_str = r_file.encode()
    str_for_hash = f"blob {file_size}\0"
    str_for_hash += r_file
    str_for_hash = str_for_hash.encode()
    print(r_file)
    print(str_for_hash)
    #sha1obj = uhashlib.sha1()
    sha1obj = uhashlib.sha1(str_for_hash)
    hexdigest = sha1obj.hexdigest()
    o_file.close()
    print(hexdigest)
    return hexdigest

def main():
    #print(tree)
    #dirs, files = parse_git_tree(tree)
    #print(dirs, files)
    app_tree = get_app_tree()
    print(app_tree)
    dirs, files = parse_git_tree(app_tree)
    print(dirs, files)
    internal_tree = build_internal_tree()
    print(internal_tree)

if __name__ == '__main__':
   # main()
   # exit(0)
    sha = '380040e79e554b3c6e9a46be6a1d8dcd226b120b'
    root_path = "/home/medvedev/PycharmProjects/mp_ota_from_git/app/ap_templates/"
    file_name = "configured.html"
    bin_hash = get_hash(root_path+file_name)
    print(sha)
    print(bin_hash)

