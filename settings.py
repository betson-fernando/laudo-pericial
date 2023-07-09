from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(os.path.realpath(os.path.dirname(__file__)), 'configs.env')

# STATIC MAPS API SETTINGS
MAPS_API_KEY = os.environ.get('MAPS_API_KEY')
MAPS_URL = 'https://maps.googleapis.com/maps/api/staticmap'

# SHEETS IMPORTS SETTINGS