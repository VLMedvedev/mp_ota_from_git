from configs.app_config import *
from web_app.web_app import application_mode


if AUTO_START_WEBAPP:
    application_mode()

