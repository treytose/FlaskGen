import os 

class Config:
    SECRET_KEY = os.urandom(12)

class DevelopmentConfig(Config):
    PORT = 5000
    HOST = '0.0.0.0'
    DEBUG = True

    DB_HOST = ""
    DB_USER = ""
    DB_PASSWORD = ""
    DB_NAME = ""

class ProductionConfig(Config):
    PORT = 80
    HOST = '0.0.0.0'
    DEBUG = False

    DB_HOST = ""
    DB_USER = ""
    DB_PASSWORD = ""
    DB_NAME = ""



config = {
    "default": DevelopmentConfig(),
    "development": DevelopmentConfig(),
    "production": ProductionConfig()
}