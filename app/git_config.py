#file for configure variables

GITHUB_OWNER = 'VLMedvedev'
GITHUB_REPOSITORY = 'mp_ota_from_git'
GITHUB_BRANCH = 'main'
GITHUB_APP_FOLDER = 'app'
GITHUB_TOKEN = ""

# Static URLS
# GitHub uses 'main' instead of master for python repository trees
GITHUB_URL = f'https://github.com/{GITHUB_OWNER}/{GITHUB_REPOSITORY}'
GITHUB_TREES_API_URL = f'https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPOSITORY}/git/trees/'
RAW_URL = f'https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPOSITORY}/master/'

ROOT_PATH = "/"
EXCLUDE_LIST = ["__pycache__", "boot.py", "mp_git.py", "app_config.json", "wifi.json","sha1_internal_save_file.json"]


