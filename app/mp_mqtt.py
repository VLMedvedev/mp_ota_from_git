import time
import _thread
import binascii
import machine
from umqtt.simple import MQTTClient
from machine import Pin

from configs.mqtt_config import *
from configs.hw_config import HW_BT_RIGTH_UP
from configs.hw_config import HW_LED_PIN
# Many ESP8266 boards have active-low "flash" button on GPIO0.
button = Pin(HW_BT_RIGTH_UP, Pin.IN, Pin.PULL_UP)
led = Pin(HW_LED_PIN, Pin.OUT, value=1)
# Default MQTT server to connect to
#SERVER = "192.168.1.35"


state = 0

def sub_cb(topic, msg):
    global state
    print((topic, msg))
    if msg == b"on":
        led.value(1)
        state = 0
    elif msg == b"off":
        led.value(0)
        state = 1
    elif msg == b"toggle":
        # LED is inversed, so setting it to current state
        # value will make it toggle
        led.value(state)
        state = 1 - state

def mqtt_main():
    """ client_id,
        server,
        port=0,
        user=None,
        password=None,
        keepalive=0,
        ssl=None,
    """
    if CLIENT_ID=="machine_id":
        client_id = binascii.hexlify(machine.unique_id())
    else:
        client_id = CLIENT_ID

    #TOPIC = b"led"
    topic = bytes(TOPIC, 'utf-8')

    c = MQTTClient(client_id,
                   SERVER,
                   PORT,
                   USER,
                   PASSWORD,
                   KEEPALIVE,
              #     SSL,
                   )
    # Subscribed messages will be delivered to this callback
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(topic)
    print("Connected to %s, subscribed to %s topic" % (SERVER, topic))

    while True:
        while True:
            c.check_msg()
            if button.value() == 0:
                break
            time.sleep_ms(20)
        print("Button pressed")
        pub_topic = TOPIC.replace("#","")
        pub_topic += "led"
        pub_topic = bytes(pub_topic, 'utf-8')
        c.publish(pub_topic, b"toggle")
        time.sleep_ms(200)
    c.disconnect()


def main():
    print("start mqtt")
    mqtt_th = _thread.start_new_thread(mqtt_main, ())
    print("wait")
    time.sleep(5)

