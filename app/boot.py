# highly recommended to set a lowish garbage collection threshold
# to minimise memory fragmentation as we sometimes want to
# allocate relatively large blocks of ram.
import gc, os
from configs.app_config import *
from  wifi_portal import start_wifi

def main():
    """Main function. Runs after board boot, before main.py
    Connects to Wi-Fi and checks for latest OTA version.
    """
    #gc.set_threshold(50000)
    gc.collect()
    gc.enable()

    if AUTO_CONNECT_TO_WIFI_AP:
        start_wifi()


#if __name__ == "__main__":
main()
