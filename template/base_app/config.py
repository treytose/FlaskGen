import os 

class Config:
    SECRET_KEY = os.urandom(12)

class DevelopmentConfig(Config):
    PORT = 5000
    HOST = '0.0.0.0'
    DEBUG = True

    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

class ProductionConfig(Config):
    PORT = 5500
    HOST = '0.0.0.0'
    DEBUG = False

    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")



config = {
    "default": ProductionConfig(),
    "development": DevelopmentConfig(),
    "production": ProductionConfig()
}
