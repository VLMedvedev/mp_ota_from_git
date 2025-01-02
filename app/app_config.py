#value
from micropython import const

AP_NAME = "Battery monitor"
AP_DOMAIN = "power-storage.eu"
AP_TEMPLATE_PATH = "ap_templates"

AUTO_UPDATE_FROM_GIT = True
AUTO_RESTART_AFTER_UPDATE = False
AUTO_CONNECT_TO_WIFI_AP = True
WIFI_MAX_ATTEMPTS = 3
AUTO_START_WEBREPL = False
AUTO_START_WEBAPP = True
AUTO_START_SETUP_WIFI = True
REBUILD_SHA1_INTERNAL_FILE = False

WIFI_FILE = "/wifi.json"
WIFI_MAX_ATTEMPTS = 3
REBUILD_FILE_FLAG = "/rebuild_file_flag"

HW_LED_PIN = const(15)

