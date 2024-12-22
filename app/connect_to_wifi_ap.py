from phew import connect_to_wifi, is_connected_to_wifi
import os

def start_wifi():
    # Figure out which mode to start up in...
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
                    break
                else:
                    wifi_current_attempt += 1

            if is_connected_to_wifi():
                import webrepl

                webrepl.start()
                # import main_webrepl
                # main_webrepl.start_turn()
                application_mode()
            else:

                # Bad configuration, delete the credentials file, reboot
                # into setup mode to get new credentials from the user.
                print("Bad wifi connection!")
                print(wifi_credentials)
                #  os.remove(WIFI_FILE)
                machine_reset()

    except Exception:
        # Either no wifi configuration file found, or something went wrong,
        # so go into setup mode.
        setup_mode()