from os.path import join, dirname, realpath
from os import environ
from dotenv import load_dotenv


dotenv_path = join(realpath(dirname(__file__)), 'configs.env')
load_dotenv(dotenv_path=dotenv_path)

# STATIC MAPS API SETTINGS
MAPS_API_KEY = environ.get('MAPS_API_KEY')
MAPS_URL = 'https://maps.googleapis.com/maps/api/staticmap'
LOW_ZOOM = 17
HIGH_ZOOM = 20


# SHEETS IMPORTS SETTINGS
MAIN_SHEET_URL = environ.get('MAIN_SHEET_URL')
FORMS_URL = environ.get('FORMS_URL')
