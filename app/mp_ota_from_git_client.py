#import urequests
import requests as urequests
import json
from git_config import GITHUB_TOKEN, GITHUB_BRANCH, GITHUB_TREES_API_URL, GITHUB_APP_FOLDER

app_trees_url_sha = None

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



#print(tree)
#dirs, files = parse_git_tree(tree)
#print(dirs, files)
app_tree = get_app_tree(tree)
print(app_tree)
dirs, files = parse_git_tree(app_tree)
print(dirs, files)