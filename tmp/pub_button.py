import time
import binascii
import machine
from umqtt.simple import MQTTClient
from machine import Pin

from configs.mqtt_config import SERVER
from configs.hw_config import HW_BT_RIGTH_UP

# Many ESP8266 boards have active-low "flash" button on GPIO0.
button = Pin(HW_BT_RIGTH_UP, Pin.IN, Pin.PULL_UP)

# Default MQTT server to connect to
#SERVER = "192.168.1.35"
CLIENT_ID = binascii.hexlify(machine.unique_id())
TOPIC = b"led"

def pub_main(server=SERVER):
    c = MQTTClient(CLIENT_ID, server)
    c.connect()
    print("Connected to %s, waiting for button presses" % server)
    while True:
        while True:
            if button.value() == 0:
                break
            time.sleep_ms(20)
        print("Button pressed")
        c.publish(TOPIC, b"toggle")
        time.sleep_ms(200)

    c.disconnect()
