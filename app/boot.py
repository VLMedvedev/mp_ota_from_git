import gc
import os
import json
from phew import connect_to_wifi, is_connected_to_wifi
import machine

#import upip

APP_CONFIG_FILE = "app_config.json"
WIFI_FILE = "wifi.json"
WIFI_MAX_ATTEMPTS = 3

def get_app_config():
    try:
        print("Testing saved wifi credentials...")
        os.stat(APP_CONFIG_FILE)
        # File was found, attempt load...
        with open(APP_CONFIG_FILE) as f:
            app_config = json.load(f)
            print(app_config)
            return app_config
    except Exception:
        # Either no app configuration file found, or something went wrong,
        # return default config.
        default_config = {
              "auto_update_from_git" : :True,
              "auto_connect_to_wifi_ap" : :True,
              "wifi_max_attempts" : 3,
              "auto_start_webrepl" : :True,
              "auto_start_webapp" : :True,
              "auto_start_setup_wifi" : :True,
            }
        return default_config

def attemps_connect_to_wifi():
    try:
        print("Testing saved wifi credentials...")
        os.stat(WIFI_FILE)
        # File was found, attempt to connect to wifi...
        with open(WIFI_FILE) as f:
            wifi_current_attempt = 1
            wifi_credentials = json.load(f)
            print(wifi_credentials)
            while (wifi_current_attempt < WIFI_MAX_ATTEMPTS):
                ip_address = connect_to_wifi(wifi_credentials["ssid"], wifi_credentials["password"])
                print(ip_address)
                if is_connected_to_wifi():
                    print(f"Connected to wifi, IP address {ip_address}")
                    return ip_address
                else:
                    wifi_current_attempt += 1
        return None
    except Exception:
        # Either no wifi configuration file found, or something went wrong,
        # so go into setup mode.
        return None


def main():
    """Main function. Runs after board boot, before main.py
    Connects to Wi-Fi and checks for latest OTA version.
    """
    gc.collect()
    gc.enable()

    ip_address = None
    app_config = get_app_config()
    if app_config["auto_connect_to_wifi_ap"]:
        ip_address = attemps_connect_to_wifi()
    app_update = False
    if app_config["auto_update_from_git"] and ip_address not is None:
        app_update = OTA.update()
    if app_update:
        print("Updated to the latest version! Rebooting...")
        machine.reset()


if __name__ == "__main__":
    main()
