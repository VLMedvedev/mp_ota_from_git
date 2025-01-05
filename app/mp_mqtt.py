#import asyncio
from primitives import Queue
import time
import _thread
import binascii
import machine

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
mqtt_pub_queue = Queue()

def sub_cb(topic, msg):
    global state
    print((topic, msg))
    print(topic.decode(), msg.decode())
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

def pub_mqtt(msg, topic=None):
    if topic is None:
        topic = PUBLISH_TOPIC
    mqtt_pub_queue.put((msg, topic))

class UMQTT_class():
    def __init__(self,
                client_id,
                server,
                port=0,
                user=None,
                password=None,
                keepalive=0,
                ssl=None,
                topic_subscribe="mp_mqtt/#",
                topic_publish="mp_mqtt/pub",
                check_period_sec=3,
                mqtt_pub_queue = None
                         ):

        from umqtt.simple import MQTTClient
        self.mqtt_cli = MQTTClient(client_id,
                                 server,
                                 port,
                                 user,
                                 password,
                                 keepalive,
                       )

        self.mqtt_pub_queue = mqtt_pub_queue
        self.check_period_sec = check_period_sec
        self.topic_subscribe = bytes(topic_subscribe, 'utf-8')
        # Subscribed messages will be delivered to this callback
        self.mqtt_cli.set_callback(sub_cb)
        self.mqtt_cli.connect()
        self.mqtt_cli.subscribe(self.topic_subscribe)
        print("Connected to %s, subscribed to %s topic" % (server, self.topic_subscribe))
        self.working = True
        #self.run()

    def start(self):
        while self.working:
            self.mqtt_cli.check_msg()
            if not self.mqtt_pub_queue.empty():
                q_msg, q_topic = self.mqtt_pub_queue.get()
                msg = bytes(q_msg, 'utf-8')
                topic = bytes(q_topic, 'utf-8')
                self.mqtt_cli.publish(topic, msg)
            time.sleep(self.check_period_sec)
        self.stop()

    def stop(self):
        self.working = False
        self.mqtt_cli.disconnect()


def mqtt_start():
    client_id = CLIENT_ID
    if CLIENT_ID=="machine_id":
        client_id = binascii.hexlify(machine.unique_id())

    umqtt_cli = UMQTT_class(client_id,
                            SERVER,
                            PORT,
                            USER,
                            PASSWORD,
                            KEEPALIVE,
                            SSL,
                            SUBSCRIBE_TOPIC,
                            PUBLISH_TOPIC,
                            CHECK_PERIOD_SEC,
                            mqtt_pub_queue,
                            )
    time.sleep(3)
    umqtt_cli.start()

    while True:
        while True:
            if button.value() == 0:
                break
            time.sleep_ms(20)
        pub_mqtt("toggle", "mp_mqtt/led")
        print("Button pressed")
        time.sleep_ms(200)


def main():
    print("start mqtt")
    mqtt_th = _thread.start_new_thread(mqtt_start, ())
    print("wait")
    time.sleep(3)

