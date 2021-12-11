#!venv/bin/python
import argparse
from app import create_app


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Enter the name of the config object to use", default="default")
    args = parser.parse_args()    

    app = create_app(args.config)
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'), debug=app.config.get('DEBUG'))