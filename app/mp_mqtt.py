import time
from umqtt.pub_button import pub_main
from umqtt.sub_led import  sub_main
import _thread

def main():
    print("start mqtt")
    sub_mqtt_th = _thread.start_new_thread(sub_main, ())
    pub_mqtt_th = _thread.start_new_thread(pub_main, ())
    pub_main()
   # while True:
    print("wait")
    time.sleep(5)

