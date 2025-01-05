import threading
import time

from umqtt import sub_led, pub_button
import _thread

def main():
    print("start mqtt")
    sub_mqtt_th = threading.Thread(target=sub_led, args=())
    pub_mqtt_th = threading.Thread(target=pub_button, args=())
    sub_mqtt_th.start()
    pub_mqtt_th.start()
    while True:
        print("wait")
        time.sleep(5)

