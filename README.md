# backend
A backend for providing necessary data to All Ears' mobile app and website.


# Structure
Displayed below is the structure of our project.

    main.py
    app/
        __init__.py
        models.py
        routes.py
        templates/
        static/
    instance/
        config.py

All of the source code will go in the `app` folder. 

All of the configuration files should go in the `instance` folder. It should contain a `config.py` file that defines all of the environment-dependent variables that our application will need to run. It should never be added to source control. It will contain things like the server's secret key, database usernames and passwords, and whether or not the app is running in a production environment. An example config is provided in `example_config.py`. It has all of the variables that the server will need to run.

# Running the for development
First, make sure all dependencies are installed.

    pipenv install --dev

Then, set the environment variables for the Flask development server.

    export FLASK_APP=app
    export FLASK_ENV=development

Lastly, run the app.

    pipenv run python -m flask run

In development mode, the Flask development server will reload automatically when your code changes.

