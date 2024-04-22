from dotenv import load_dotenv, find_dotenv
from os import environ
from pathlib import Path
import sys
from .Classes import Local

load_dotenv(find_dotenv('configs.env'))