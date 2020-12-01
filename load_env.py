from dotenv import load_dotenv
from sys import platform


def load_env():
    if platform == "darwin":
        load_dotenv(dotenv_path='.docker/.env')
    else:
        load_dotenv()
