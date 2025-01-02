#value
from micropython import const

AP_NAME = "Battery monitor"
AP_DOMAIN = "power-storage.eu"
AP_TEMPLATE_PATH = "ap_templates"

AUTO_UPDATE_FROM_GIT = False
AUTO_RESTART_AFTER_UPDATE = False
AUTO_CONNECT_TO_WIFI_AP = False
WIFI_MAX_ATTEMPTS = 3
AUTO_START_WEBREPL = False
AUTO_START_WEBAPP = False
AUTO_START_SETUP_WIFI = False
REBUILD_SHA1_INTERNAL_FILE = False

WIFI_FILE = "/configs/wifi_ap.py"
WIFI_MAX_ATTEMPTS = 3
REBUILD_FILE_FLAG = "/rebuild_file_flag"

HW_LED_PIN = const(15)
