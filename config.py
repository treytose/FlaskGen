import os
class Config:
    APP_PATH = "PATH/TO/MY/FLASK/APP"
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = "DB"
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    
