import urequests
import uhashlib
import os
import time
import json
from git_config import GITHUB_TOKEN, GITHUB_BRANCH, GITHUB_TREES_API_URL, GITHUB_APP_FOLDER, RAW_URL, ROOT_PATH

app_trees_url_sha = None

def pull(f_path ):
    print(f'pulling {f_path} from github')
    os.chdir(ROOT_PATH)
    headers = {'User-Agent': 'mp_ota_from_git'}
    # ^^^ Github Requires user-agent header otherwise 403
    if GITHUB_TOKEN != "":
      headers['authorization'] = "bearer %s" % GITHUB_TOKEN
    raw_url = f"{RAW_URL}{GITHUB_APP_FOLDER}/{f_path}"
    r = urequests.get(raw_url, headers=headers)
    try:
        file_type = r.headers['content-type']
        if file_type.find("text") >= 0:
            content = r.content.decode('utf-8')
            new_file = open(f_path, 'w')
        else:
            content = r.content
            new_file = open(f_path, 'wb')

        new_file.write(content)
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

def get_app_tree(tree=None):
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

def build_internal_tree():
    internal_tree = {}
    exclude_list = ["__pycache__", "boot.py", "mp_git.py"]
    os.chdir(ROOT_PATH)
    for item in os.listdir():
        if not item in exclude_list:
            add_to_tree(item, internal_tree)
    return internal_tree

def add_to_tree(dir_item, internal_tree):
   # print(dir_item)
    curent_path = os.getcwd()
    if curent_path != ROOT_PATH:
        file_path = curent_path + '/' + dir_item
    else:
        file_path = curent_path + dir_item
    #print(f'sub_path: {file_path}')
    if is_directory(file_path) and len(os.listdir(file_path)) >= 1:
        os.chdir(file_path)
        for i in os.listdir():
            add_to_tree(i, internal_tree)
        os.chdir('..')
    else:
        try:
            subfile_path = file_path.replace(ROOT_PATH, "")
            internal_tree[subfile_path] = get_hash(file_path)
        except OSError: # type: ignore # for removing the type error indicator :)
            print(f'{dir_item} could not be added to tree')

def update():
    update_list = []
    log = []
    os.chdir(ROOT_PATH)
    git_app_tree = get_app_tree()
    print(git_app_tree)
    if git_app_tree is None:
        return None
    git_app_tree_list = git_app_tree.get('tree',[])
    if git_app_tree_list is None:
        return None
    internal_tree = build_internal_tree()
    for git_file_dict in git_app_tree_list:
        if git_file_dict.get('type') == 'blob':
            file_path = git_file_dict.get('path')
            file_sha1 = git_file_dict.get('sha')
            internal_sha1 = internal_tree.pop(file_path, None)
            if internal_sha1 is None:
                update_list.append(file_path)
                continue
            if file_sha1 != internal_sha1:
                update_list.append(file_path)
                #internal_tree.pop(file_path)

        elif git_file_dict.get('type') == 'tree':
            dir_path = git_file_dict.get('path')
            try:
                os.mkdir(dir_path)
                log_str = f'{dir_path} file removed from int mem'
                log.append(log_str)
            except:
                print(f'failed to {dir_path} dir may already exist')

    print(internal_tree)
    for file_name in internal_tree:
        if is_directory(file_name):
            continue
        try:
            os.remove(file_name)
            log.append(f'{file_name} file removed from int mem')
        except:
            log.append(f'{file_name} del failed from int mem')
            print('failed to delete old file')

    print(update_list)
    for file_name in update_list:
      try:
        pull(file_name)
        log.append(file_name + ' updated')
      except:
        log.append(file_name + ' failed to pull')

    logfile = open('ugit_log.py','w')
    logfile.write(str(log))
    logfile.close()
    time.sleep(5)
    if len(update_list) > 0:
        return True
    return False


def get_hash(file_name):
   # print(file_name)
    #file_stats = os.stat(file_name)
    #file_size = file_stats.st_size
    try:
        with   open(file_name, mode='rb') as o_file:
            content = o_file.read()
            header = f"blob {len(content)}\0".encode('utf-8')
            data = header + content
            # Calculate SHA-1 hash
            sha1_hash = uhashlib.sha1(data).hexdigest()
          #  print(sha1_hash)
            return sha1_hash
    except:
        return None


def main():
    update()

if __name__ == '__main__':
    main()

   #file_n = "text-16.pf"
   #file_n = "main.py"
   #pull(file_n)



