# Kevin McAleer
# 28 Aug 2022

from phew import logging, server
from phew.template import render_template
from app_config import *
import machine
import utime
import os
import _thread

def machine_reset():
    utime.sleep(3)
    print("Resetting...")
    machine.reset()

def application_mode():
    print("Entering application mode.")
    CSS_STYLE = None
    onboard_led = machine.Pin(HW_LED_PIN, machine.Pin.OUT)

    def app_index(request):
        #return render_template(f"{APP_TEMPLATE_PATH}/home.html")
        return render_template(f"/{APP_TEMPLATE_PATH}/index2.html",
                               title=AP_NAME,
                               style_css_str=CSS_STYLE, )

    def app_toggle_led(request):
        led_on = onboard_led.value()
        if not led_on:
            onboard_led.on()
        else:
            onboard_led.off()
        return "OK"

    def app_get_temperature(request):
        # Not particularly reliable but uses built in hardware.
        # Demos how to incorporate senasor data into this application.
        # The front end polls this route and displays the output.
        # Replace code here with something else for a 'real' sensor.
        # Algorithm used here is from:
        # https://www.coderdojotc.org/micropython/advanced-labs/03-internal-temperature/
        # sensor_temp = machine.ADC(4)
        # reading = sensor_temp.read_u16() * (3.3 / (65535))
        temperature = 27  # - (reading - 0.706)/0.001721
        return f"{round(temperature, 1)}"

    def app_reset(request):
        # Deleting the WIFI configuration file will cause the device to reboot as
        # the access point and request new configuration.
        os.remove(WIFI_FILE)
        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template(f"{APP_TEMPLATE_PATH}/reset.html", access_point_ssid=AP_NAME)

    def app_reboot(request):
        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template(f"{APP_TEMPLATE_PATH}/reboot.html", access_point_ssid=AP_NAME)

    def app_catch_all(request):
        return "Not found.", 404

    def about(request):
        return render_template(f"/{APP_TEMPLATE_PATH}/about.html", name="Vladimir",
                               title="About this Site",
                               style_css_str=CSS_STYLE, )

    def login_form(request):
        print(request.method)
        if request.method == 'GET':
            return render_template(f"/{APP_TEMPLATE_PATH}/login.html")
        if request.method == 'POST':
            username = request.form.get("username", None)
            password = request.form.get("password", None)

            if username == "vladimir" and password == "password":
                return render_template(f"/{APP_TEMPLATE_PATH}/default.html",
                                       content=f"<h1>Welcome back, {username}</h1>",
                                       style_css_str=CSS_STYLE)
            else:
                return render_template(f"/{APP_TEMPLATE_PATH}/default.html",
                                       content="Invalid username or password",
                                       style_css_str=CSS_STYLE)

    def get_css():
        with open(f"/{APP_TEMPLATE_PATH}/style.css", "r") as f:
            style_str = f.read()
            return style_str

    server.add_route("/", handler=app_index, methods=["GET"])
    server.add_route("/toggle", handler=about, methods=["GET"])
    server.add_route("/about", handler=app_toggle_led, methods=["GET"])
    server.add_route("/login", handler=login_form, methods=["POST",'GET'])
    server.add_route("/temperature", handler=app_get_temperature, methods=["GET"])
    server.add_route("/reset", handler=app_reset, methods=["GET"])
    server.add_route("/reboot", handler=app_reboot, methods=["GET"])
    # Add other routes for your application...
    server.set_callback(app_catch_all)
    CSS_STYLE = get_css()




