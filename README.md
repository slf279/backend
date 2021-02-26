# Capstone Backend

A JSON REST API for providing necessary data to All Ears' mobile app and website.

# Structure

Displayed below is the structure of our project.

    main.py
    app/
        __init__.py
        auth.py
        data_access.py
        models.py
        routes.py

    instance/
        config.json
        password.txt
    
    example_deployment_files/
        example_app_config.json
        example_nginx_site.conf
        example_service_file.service
        example_uwsgi.ini

    init_schema.sql
    set_password.py
    requirements.txt
    ...

The executable for the app will go in the `main.py` file. This is the file that should be run by the Flask development server or a WSGI or UWSGI application.

The non-executable library file will go in the app folder. `init.py` contains the app factory and handles all of the configuration loading. `auth.py` contains the logic that will limit API access and tracks login state. `data_access.py` contains all code that will interact with nonvolatile storage (database and file system) during application execution. `models.py` contains the data and service provider models for the application. `routes.py` contains the code that directly deals with requests at certain URL routes.

All files that will change based on where the app is run will go in the `instance` folder. This includes app configuration values in the `config.json` file. That file will need to be written by the user. All fields present in `example_config.json` must be included. A hash of the master password using Argon2id must be included in the `password.txt` file. The file `set_password.py` was written for this purpose and can be used as follows:

    python set_password.py [password]

The `init_schema.sql` file will be used in the initial setup and structure of the database. It should be run before the app is deployed.

All the dependencies for the project are in the `requirements.txt` file.

# Running the for development

First, make sure all dependencies are installed.

    pip install -r requirements.txt

Then, set the environment variables for the Flask development server.
    
    # Bash 
    export FLASK_APP=main
    export FLASK_ENV=development

    # Powershell
    $Env:FLASK_APP = "main"
    $Env:FLASK_ENV = "development"

    :: Command Line
    set FLASK_APP=main
    set FLASK_ENV=development

Lastly, run the app.

    python -m flask run

In development mode, the Flask development server will reload automatically when your code changes.

# API Endpoint Documentation

All REST API documentation for each of the URL Endpoints are in [API_DOCS.md](./API_DOCS.md).

# Deployment
In order to deploy the app one will need MariaDB version 10.5 (other versions not tested) installed on one's system 
along with MariaDB Connector/C. On Ubuntu, one should install the `mariadb-server` package from MariaDB's official 
repository (instructions [here](https://mariadb.org/download/)). In order to use the MariaDB Connector/C with Python's
connector package `mariadb` one will need to install the development library for MariaDB (`libmariadb-dev` on Ubuntu).

After installing all system requirements, one must then install first the `wheel` then `uwsgi` Python packages and make 
a file named `wsgi.py`. It should have these contents:

    from main import app
    
    if __name__ == "__main__":
        app.run()

After doing all that, one will need to create an `.ini` file for one's uwsgi and a service file. Examples are provided 
in the `deployment_example_files` directory. After this one needs to write one's NGINX site config file. We use reverse
proxy in our example. Open the firewall, start the service, reload NGINX and the app is deployed!