from phew import access_point, connect_to_wifi, is_connected_to_wifi, dns, server
from phew.template import render_template
import json
import network
import os
import utime
import _thread
from configs.app_config import *
from app_templates.web_app import application_mode, machine_reset
from configs.constants_saver import ConstansReaderWriter

def setup_mode():
    print("Entering setup mode...")

    def scan_wifi_ap():
        ap_str = ""
        wlan_sta = network.WLAN(network.STA_IF)
        wlan_sta.active(True)
        id = 0
        for ssid, *_ in wlan_sta.scan():
            ssid_str = ssid.decode("utf-8").strip()
            if len(ssid_str) == 0:
                continue
            id += 1
            print(ssid_str)
            ap_str += f"""<input type="radio" name="ssid" value="{ssid_str}" id="{id}"><label for="{ssid_str}">&nbsp;{ssid_str}</label><br>"""

        return ap_str

    def ap_index(request):
        if request.headers.get("host").lower() != AP_DOMAIN.lower():
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = AP_DOMAIN.lower())

        return render_template(f"{AP_TEMPLATE_PATH}/index.html", ap_str = scan_wifi_ap(), replace_symbol=False)

    def ap_configure(request):
        print("Saving wifi credentials...")
        crw = ConstansReaderWriter("wifi")
        crw.set_constants_from_config_dict(request.form)
        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template(f"{AP_TEMPLATE_PATH}/configured.html", ssid = request.form["ssid"])
        
    def ap_catch_all(request):
        if request.headers.get("host") != AP_DOMAIN:
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = AP_DOMAIN)

        return "Not found.", 404

    #ap_str = scan_wifi_ap()
    #print(ap_str)

    server.add_route("/", handler = ap_index, methods = ["GET"])
    server.add_route("/configure", handler = ap_configure, methods = ["POST"])
    server.set_callback(ap_catch_all)

    ap = access_point(AP_NAME)
    ip = ap.ifconfig()[0]
    dns.run_catchall(ip)

def get_rebuild_flag():
    try:
        os.stat(REBUILD_FILE_FLAG)
        return True
    except:
        return False

def set_rebuild_file_flag():
    ff = open(REBUILD_FILE_FLAG, "w")
    ff.write("1")
    ff.close()


def start_wifi():
    # Figure out which mode to start up in...
    try:
        print("Testing saved wifi credentials...")
        os.stat(WIFI_FILE)
        from configs.wifi import SSID, PASSWORD

        while (wifi_current_attempt < WIFI_MAX_ATTEMPTS):
            ip_address = connect_to_wifi(SSID, PASSWORD)
            print(ip_address)
            if is_connected_to_wifi():
                print(f"Connected to wifi, IP address {ip_address}")
                break
            else:
                wifi_current_attempt += 1

        if is_connected_to_wifi():
            app_update = False
            if AUTO_UPDATE_FROM_GIT:
                import mp_git
                rebuild = False
                if REBUILD_SHA1_INTERNAL_FILE or get_rebuild_flag():
                    rebuild = True
                app_update = mp_git.update(rebuild)
            if app_update:
                set_rebuild_file_flag()
                if AUTO_RESTART_AFTER_UPDATE:
                    print("Updated to the latest version! Rebooting...")
                    utime.sleep(3)
                    #_thread.start_new_thread(machine_reset, ())
                    machine_reset()
            if AUTO_START_WEBREPL:
                import webrepl
                webrepl.start()
            # # import main_webrepl
            # # main_webrepl.start_turn()
            if AUTO_START_WEBAPP:
                application_mode()
        else:
            if AUTO_START_SETUP_WIFI:
                # Bad configuration, delete the credentials file, reboot
                # into setup mode to get new credentials from the user.
                print("Bad wifi connection!")
                print(wifi_credentials)
                os.remove(WIFI_FILE)
                machine_reset()

    except Exception:
        if AUTO_START_SETUP_WIFI:
            # Either no wifi configuration file found, or something went wrong,
            # so go into setup mode.
            setup_mode()
    if AUTO_START_WEBAPP or AUTO_START_SETUP_WIFI:
        # Start the web server...
        server.run()


if __name__ == "__main__":
    start_wifi()