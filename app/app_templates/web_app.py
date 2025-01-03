# Kevin McAleer
# 28 Aug 2022

from phew import logging, server
from phew.template import render_template
from configs.app_config import *
import machine
import utime
import os
import _thread
from configs.constants_saver import ConstansReaderWriter

def machine_reset():
    utime.sleep(3)
    print("Resetting...")
    machine.reset()

def application_mode():
    print("Entering application mode.")
    CSS_STYLE = None
    onboard_led = machine.Pin(HW_LED_PIN, machine.Pin.OUT)

    def app_index(request):
        #return render_template("/app_templates/home.html")
        return render_template("/app_templates/index2.html",
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
        return render_template("/app_templates/reset.html", access_point_ssid=AP_NAME)

    def app_reboot(request):
        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template("/app_templates/reboot.html", access_point_ssid=AP_NAME)

    def app_catch_all(request):
        return "Not found.", 404

    def about(request):
        return render_template("/app_templates/about.html",
                               title="About this Site",
                               style_css_str=CSS_STYLE, )

    def login_form(request):
        print(request.method)
        if request.method == 'GET':
            return render_template("/app_templates/login.html")
        if request.method == 'POST':
            username = request.form.get("username", None)
            password = request.form.get("password", None)

            if username == "vladimir" and password == "password":
                return render_template("/app_templates/default.html",
                                       content=f"<h1>Welcome back, {username}</h1>",
                                       style_css_str=CSS_STYLE)
            else:
                return render_template("/app_templates/default.html",
                                       content="Invalid username or password",
                                       title="About this Site",
                                       style_css_str=CSS_STYLE)

    def get_config_page(app_config_dict):
        config_page = ""
        max_var_len = 0
        for var_name in app_config_dict.keys():
            if len(var_name) > max_var_len:
                max_var_len = len(var_name)
        for var_name, val in app_config_dict.items():
            print(f"{var_name}: {val}")
            type_attr = type(val)
            checked = ""
            # print(var_name, type_attr)
            if type_attr == str:
                type_input = "text"
            elif type_attr == int:
                type_input = "number"
            elif type_attr == float:
                type_input = "number"
            elif type_attr == bool:
                type_input = "checkbox"
                if val:
                    checked = 'checked'

            var_name = var_name.replace(":", "")
            var_len = len(var_name)
            label_name = var_name
            for i in range(max_var_len - var_len):
                label_name += "."

            str_http = f'''<label for="{var_name}">&nbsp;{label_name}:</label>            
                          <input type="{type_input}" id="{var_name}" name="{var_name}" value="{val}"  {checked} "><br>
                         '''
            config_page += str_http
            config_page += "\n"

        return config_page

    def config_page(request):
        print(request.method)
        module_config = "app_config"
        crw = None
        crw = ConstansReaderWriter(module_config)
        app_config_dict = crw.get_dict()
        if request.method == 'GET':
            config_page = get_config_page(app_config_dict)
            return render_template("/app_templates/config_page.html",
                                   config_page=config_page,
                                   page_info="Please save params",
                                   title="Config page",
                                   style_css_str=CSS_STYLE,
                                   replace_symbol=False)
        if request.method == 'POST':
            config_page_dict = request.form
         #   print(config_page_dict)
          #  print(app_config_dict)
            for var_name, val in app_config_dict.items():
                type_attr = type(val)
                if type_attr == bool:
                    page_val = config_page_dict.get(var_name, False)
                    if page_val:
                        config_page_dict[var_name] = 'True'
                    else:
                        config_page_dict[var_name] = 'False'

        #    print(config_page_dict)
            crw.set_constants_from_config_dict(config_page_dict)
            app_config_dict = crw.get_dict()
            utime.sleep(2)
            config_page = get_config_page(app_config_dict)
            return render_template("/app_templates/config_page.html",
                                   config_page=config_page,
                                   page_info="Params saved !!!",
                                   title="Config page",
                                   style_css_str=CSS_STYLE,
                                   replace_symbol=False)

    def get_css():
        with open("/app_templates/style.css", "r") as f:
            style_str = f.read()
            return style_str

    CSS_STYLE = get_css()
    server.add_route("/", handler=app_index, methods=["GET"])
    server.add_route("/toggle", handler=app_toggle_led, methods=["GET"])
    server.add_route("/about", handler=about, methods=["GET"])
    server.add_route("/login", handler=login_form, methods=["POST",'GET'])
    server.add_route("/temperature", handler=app_get_temperature, methods=["GET"])
    server.add_route("/reset", handler=app_reset, methods=["GET"])
    server.add_route("/reboot", handler=app_reboot, methods=["GET"])
    server.add_route("/config_page", handler=config_page, methods=["POST",'GET'])
    server.add_route("/app_config", handler=app_config, methods=["POST",'GET'])
    server.add_route("/sys_config", handler=sys_config, methods=["POST",'GET'])
    # Add other routes for your application...
    server.set_callback(app_catch_all)





