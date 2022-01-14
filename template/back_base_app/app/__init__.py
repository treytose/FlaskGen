from flask import Flask
from config import config

# declare libraries #


def create_app(config_name="default"):
    app = Flask(__name__)

    config_name = config_name if config_name and config_name in config else "default"
    app.config.from_object(config[config_name])

    # init libraries #


    # import blueprints #
    from app.home import homeBP

    # register blueprints #
    app.register_blueprint(homeBP)

    return app