# Databases
# Digital Ocean
from dotenv import load_dotenv
import pathlib
import os

load_dotenv()

ROOT_DIR = pathlib.Path.cwd()
LOCAL_FTP_PATH = ROOT_DIR.joinpath("data", "ftp")
WEBDRIVER_PATH = ROOT_DIR.joinpath("chromedriver.exe")


MMS_CREDENTIALS = {
    'username': os.environ.get('USER'),
    'password': os.environ.get('PASSWORD')
}

