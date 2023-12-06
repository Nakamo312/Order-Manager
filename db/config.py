import os

from dotenv import load_dotenv

load_dotenv()
HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
USER = os.environ.get("USER")
PASSWORD = os.environ.get("PASSWORD")
DB_NAME = os.environ.get("DB_NAME")