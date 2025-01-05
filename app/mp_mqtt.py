import time
from umqtt import sub_led, pub_button
import _thread

def main():
    print("start mqtt")
    sub_mqtt_th = _thread.start_new_thread(sub_led, ())
    pub_mqtt_th = _thread.start_new_thread(pub_button, ())
   # while True:
    print("wait")
    time.sleep(5)

