#!/usr/local/bin/python3.9
import sys, subprocess, os, shutil, re
from flask_gen_config import FlaskGenConfig
from lib.p3tools import p3db

config = FlaskGenConfig()
BASE_DIR = os.getcwd()

######## Helpers ########
def load_flask_application():
    if not config.APP_PATH:
        app_path = input("Enter path to base application (e.g. /path/to/my/app): ")
        if input("Would you like to save this application as the default? (y/n) ") == "y":
            search_and_replace(os.path.join(BASE_DIR, "flask_gen_config.py"), 'APP_PATH =', f'APP_PATH = "{app_path}"', whole_line=True)
            print("Application saved and will be loaded by default")
    else:
        app_path = config.APP_PATH
    
    sys.path.append(app_path)

    # activate the Flask app environment #
    os.chdir(app_path)
    print("changed working directory to: ", os.getcwd())

def get_confirmed_input(question):
    user_input = input(question)
    while not input(f"confirm input '{user_input}' (y/n) ") == "y":
        user_input = input(question)
    return user_input

def get_text_template(template_name):
    with open(os.path.join(BASE_DIR, "template/" + template_name), 'r') as f:
        data = f.read()
    return data

''' Removes or applies template filters based on include value
    e.g. filter = AUTH|from flask_login import login_required
        include removes AUTH|, not include removes the entire line
'''
def apply_template_filter(filter, template_text, include=True):
    split_data = template_text.split("\n")
    for i, data in enumerate(split_data[:]):
        if filter in data:
            if not include:
                split_data.remove(data)
            else:
                split_data[i] = data.replace(filter, "")
    return "\n".join(split_data)

def get_leading_whitespace(string):
    print(string)
    leading_ws = ""
    for letter in string:
        if letter == " ":
            leading_ws += " "
        else:
            break
    return leading_ws

def insert_after(file_data, search, line):
    split_data = file_data.split("\n")
    for i, data in enumerate(split_data[:]):
        if search in data:
            split_data.insert(i+1, f"{get_leading_whitespace(data)}{line}")
    return "\n".join(split_data)

''' Search and replace all occurences within a given file
    @arg whole_line - If True, will overwrite the entire matched line with the given replace value
'''
def search_and_replace(file_path, search, replace, whole_line=False):
    with open(file_path, 'r') as file:
        file_data = file.read()
    
    if whole_line:  
        split_data = file_data.split("\n")
        for i, data in enumerate(split_data):
            if search in data:
                split_data[i] = re.sub(r'[^\s].*', replace, data)
        file_data = "\n".join(split_data)
    else:
        file_data = file_data.replace(search, replace)

    with open(file_path, 'w') as file:
        file.write(file_data)

############################

def show_menu():
    menu_items = {
        "new_app":  {
            "callback": new_app,
            "help": "Create a new Flask application"
        },
        "library": {
            "callback": library_factory,
            "help": "Create a new library"
        },        
        "blueprint": {
            "callback": blueprint_factory,
            "help": "Automatically create and add a new Flask blueprint",
        },
        "entity": {
            "callback": entity_factory,
            "help": "Added a SQL entity, APIs, and HTML forms"
        }
    }

    print("-" * 50)
    for command, item in menu_items.items():
        print("\t{:<20}".format(command), "-", item["help"])
    
    user_input = input("> ")
    if user_input in menu_items.keys():
        menu_items[user_input]["callback"]()
        show_menu()
    elif user_input != "q":
        print('\n')
        show_menu()

  
def new_app():
    os.chdir(BASE_DIR)
    app_name = get_confirmed_input("Enter app name: ")
    app_path = get_confirmed_input("Enter absolute path to app: ")  
    app_path = os.path.join(app_path, app_name)

    print("Updating default config application..")
    search_and_replace(os.path.join(BASE_DIR, "flask_gen_config.py"), 'APP_PATH =', f'APP_PATH = "{app_path}"', whole_line=True)
    config.APP_PATH = app_path
    
    print(f"Creating directory: {app_path}")
    os.mkdir(app_path)        

    print("Importing Template..")
    subprocess.run(f"cp -rf {BASE_DIR}/template/base_app/* {app_path}", shell=True, check=True) 

    print("Creating virtual environment..")        
    os.chdir(app_path)    
    subprocess.run("python3.9 -m venv venv", shell=True, check=True)

    print("upgrading pip..")
    subprocess.run("venv/bin/pip install --upgrade pip", shell=True, check=True)

    print("installing required packages..")
    subprocess.run("venv/bin/pip install -r requirements.txt", shell=True, check=True)

    print("\nApp Created Successfully")

    if input("Configure Database? (y/n) ") == "y":
        database_host = input("Database Host: ")
        database_user = input("Database Username: ")
        database_pass = input("Database Password: ")
        database_name = input("Database Name: ")

        config_path = os.path.join(app_path, "config.py")
        search_and_replace(config_path, 'DB_HOST = ""', f'DB_HOST = "{database_host}"')
        search_and_replace(config_path, 'DB_USER = ""', f'DB_USER = "{database_user}"')
        search_and_replace(config_path, 'DB_PASSWORD = ""', f'DB_PASSWORD = "{database_pass}"')
        search_and_replace(config_path, 'DB_NAME = ""', f'DB_NAME = "{database_name}"')

        print("Done.")

    print("Run the flask app using sudo ./manage.py development")
    print("\n")

def blueprint_factory():
    load_flask_application()
    os.chdir("app")

    # get the blueprint name #
    blueprint = get_confirmed_input("Blueprint Name: ")    
    url_prefix = input("URL Prefix (enter for none): ") or "/"
    include_auth = input("Include Authentication? (y/n) ") == "y"
    
    # within the app folder, create a folder for the blueprint #
    os.mkdir(blueprint)
    
    # create __init__.py, views.py, api.py for the blueprint folder #
    os.chdir(blueprint)

    init_template = get_text_template("blueprint_init_template.txt")
    init_template = init_template.replace("{blueprint}", blueprint)    
    init_template = apply_template_filter("AUTH|", init_template, include_auth)

    with open("__init__.py", "w") as f:
        f.write(init_template)        

    view_template = get_text_template("blueprint_views_template.txt")
    view_template = view_template.replace("{blueprint}", blueprint)
    view_template = apply_template_filter("AUTH|", view_template, include_auth)

    with open("views.py", "w") as f:
        f.write(view_template)

    api_template = get_text_template("blueprint_api_template.txt")
    api_template = api_template.replace("{blueprint}", blueprint)
    api_template = apply_template_filter("AUTH|", api_template, include_auth)

    with open("api.py", "w") as f:
        f.write(api_template)

    # find where you register blueprints and register the blueprint #
    load_flask_application()
    with open("app/__init__.py" , "r") as f:
        data = f.read()
    
    data = data.replace("# import blueprints #", f"# import blueprints #\n    from app.{blueprint} import {blueprint}BP")
    data = data.replace("# register blueprints #", f"# register blueprints #\n    app.register_blueprint({blueprint}BP, url_prefix='{url_prefix}')")

    with open("app/__init__.py", "w") as f:
        f.write(data)

def library_factory():
    load_flask_application()
    library = get_confirmed_input("Library File Name: ").replace(".py", "")
    class_name = get_confirmed_input("Class Name: ")
    inst_name = "o" + class_name

    lib_template = get_text_template("library_template.txt") 
    lib_template = lib_template.replace("{class_name}", class_name)
    lib_template = lib_template.replace("{library}", library)

    with open(f"lib/{library}.py", "w") as f:
        f.write(lib_template)

    # instantiate in __init__.py #
    with open("app/__init__.py", "r") as f:
        data = f.read()

    data = insert_after(data, "from config", f"from lib.{library} import {class_name}")
    data = insert_after(data, "# declare libraries #", f"{inst_name} = {class_name}()")
    data = insert_after(data, "# init libraries #", f"{inst_name}.init_app(app)")

    with open("app/__init__.py", "w") as f:
        f.write(data)
    
    print("done.")
        

def entity_factory():
    if not config.DB_HOST or not config.DB_NAME or not config.DB_USER or not config.DB_PASSWORD:
        print("A database connection is required for automatic entity generation. Edit flask_gen_config.py with database information to continue.")
        return 

    entity = get_confirmed_input("Entity Name: ") 
    available_libs = list(filter(lambda x: x.endswith(".py"), os.listdir('lib')))
    print("Available Libraries: ", available_libs)
    library = get_confirmed_input(f"Choose a library: ").replace(".py", "")   

    available_blueprints = list(filter(lambda x: ".py" not in x and x not in ("static", "templates") and "__" not in x, os.listdir('app')))
    print("Available Blueprints: ", available_blueprints)
    blueprint = get_confirmed_input("Choose a blueprint: ")

    include_all_permissions = input("Include all permissions? (y/n) ") == "y"
    include_view_permissions = include_all_permissions or input("Inlcude view permissions? (y/n) ") == "y"
    include_edit_permissions = include_all_permissions or input("Include edit permission? (y/n) ") == "y"
    include_delete_permissions = include_all_permissions or input("Include delete permissions? (y/n) ") == "y"
    include_logs = input("Include Logging? (y/n) ") == "y"
    include_testing = input("Include Testing (y/n) ") != "n"

    # TODO: Auto Create Forms #
    db = p3db.P3DB(config.DB_HOST, config.DB_USER, config.DB_PASSWORD, config.DB_NAME)
    describe = db.fetchall(f"DESCRIBE {entity}")

    primary_key = ""
    for row in describe:
        if row["Key"] == "PRI":
            primary_key = row["Field"]
            break

    # library creation #
    lib_template = get_text_template("entity_lib_template.txt")
    lib_template = lib_template.replace("{entity}", entity)
    lib_template = lib_template.replace("{entity_pk}", primary_key)
    lib_template = apply_template_filter("LOG|", lib_template, include_logs)

    load_flask_application()
    with open(f"lib/{library}.py", "r") as f:
        data = f.read()

    data = insert_after(data, "# APIs Here", lib_template)
    
    with open(f"lib/{library}.py", "w") as f:
        f.write(data)

    # retrieve the instantiated library object name #    
    inst_name = ""
    class_name = ""
    for row in data.split("\n"):
        if "class" in row:
            class_name = row.split(" ")[1].split("(")[0]
            inst_name = "o" + class_name
            break

    # API creation #    
    with open(f"app/{blueprint}/api.py", "r") as f:
        data = f.read()

    api_template = get_text_template("entity_api.txt")
    api_template = api_template.replace("{entity}", entity)
    api_template = api_template.replace("{entity_pk}", primary_key)
    api_template = api_template.replace("{blueprint}", blueprint)
    api_template = api_template.replace("{inst_name}", inst_name)
    api_template = apply_template_filter("GET_AUTH|", api_template, include=include_view_permissions)
    api_template = apply_template_filter("CREATE_AUTH|", api_template, include=include_edit_permissions)
    api_template = apply_template_filter("UPDATE_AUTH|", api_template, include=include_edit_permissions)
    api_template = apply_template_filter("DELETE_AUTH|", api_template, include=include_delete_permissions)

    data = insert_after(data, "API Routes Here", api_template)

    with open(f"app/{blueprint}/api.py", "w") as f:
        f.write(data)    

    if include_testing:
        print("Creating Automated Tests..")
        entity_test = get_text_template("entity_test.txt")
        entity_test = entity_test.replace("{library}", library)
        entity_test = entity_test.replace("{inst_name}", inst_name)
        entity_test = entity_test.replace("{class_name}", class_name)
        entity_test = entity_test.replace("{entity}", entity)
        entity_test = entity_test.replace("{entity_pk}", primary_key)

        with open(f"tests/{entity}_test.py", "w") as f:
            f.write(entity_test)
    
    print("done.")

def test():
    load_flask_application()
    with open("app/__init__.py" , "r") as f:
        data = f.read()        
    return data

if __name__ == '__main__':    
    show_menu()
    # load_flask_application()
