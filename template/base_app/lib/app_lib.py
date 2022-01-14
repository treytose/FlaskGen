import traceback
from lib.p3tools.p3db import P3DB
from lib.p3tools.liblogger import P3Log

def excHandler(func):
    def inner(self, *args, **kwargs):
        try:
            resp = func(self, *args, **kwargs)
            return resp
        except KeyError as ke:
            self.log_error('KeyError: ' + str(traceback.format_exc()))
            return {'error': 8, 'message': f'KeyError in API - Make sure you are passing the proper JSON object with correctly named keys! Error: {str(ke)}', 'data': {}}
        except Exception as e:
            self.log_error('API exception occured: ' + str(traceback.format_exc()))
            return {'error': 6, 'message': 'An unknown error occured', 'data': {}}
    return inner

class AppLib(P3Log):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = None        

    def init_app(self, app):
        self.db = P3DB(hostname=app.config.get("DB_HOST"), username=app.config.get("DB_USER"), password=app.config.get("DB_PASSWORD"), database=app.config.get("DB_NAME"))
        self.debug = app.config.get("DEBUG", False)

        