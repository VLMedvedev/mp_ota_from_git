# highly recommended to set a lowish garbage collection threshold
# to minimise memory fragmentation as we sometimes want to
# allocate relatively large blocks of ram.
import gc, os
import json

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
              "auto_update_from_git" : True,
              "auto_connect_to_wifi_ap" : True,
              "wifi_max_attempts" : 3,
              "auto_start_webrepl" : True,
              "auto_start_webapp" : True,
              "auto_start_setup_wifi" : True,
            }
        return default_config

# helper method to quickly get connected to wifi
def connect_to_wifi(ssid, password, timeout_seconds=30):
    import network, time
    info_str = f"Connect to ssid {ssid} with password {password}"
    print(info_str)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("connecting to network...")
    wlan.connect(ssid, password)
    start = time.ticks_ms()
    print(f"Start time: {start}")
    status = wlan.status()
    print(f"Status: {status}")

    while not wlan.isconnected():
        print("wlan disconected...")
        if (time.ticks_ms() - start) > (timeout_seconds * 1000):
            break
    time.sleep(0.25)

    if wlan.status() == network.STAT_GOT_IP:
        print("return ip address....")
        return wlan.ifconfig()[0]
    return None

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
                if not ip_address is None:
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
    #gc.set_threshold(50000)
    gc.collect()
    gc.enable()
    ip_address = None
    app_config = get_app_config()
    print(app_config)
    if app_config["auto_connect_to_wifi_ap"]:
        ip_address = attemps_connect_to_wifi()
        if ip_address is None:
            return None
    app_update = False
    if app_config["auto_update_from_git"]:
        import mp_git
        app_update = mp_git.update()
    if app_update:
        print("Updated to the latest version! Rebooting...")
        import machine
        machine.reset()


if __name__ == "__main__":
    main()
