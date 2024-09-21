import json
import requests
import argparse
import sqlite3
import logging
from flask import current_app, g, Flask, flash, jsonify, redirect, render_template, request, session, Response

#Other File imports: DB for database interaction, calculations, support.
from db import DB
from config import flask_key, google_key, mapbox_key


# base setup
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
# I need to understand this functionality (I currently do not)
# required for consistent session(s)?
app.secret_key = flask_key

# path to db
DATABASE = 'powermax.db'

def get_db_conn():
    """ 
    gets connection to database
    """
    if "_database" not in app.config:
        app.config["_database"] = sqlite3.connect(DATABASE)
        return app.config["_database"] 
    else:
        return app.config["_database"] 

# SITE PAGES AND WIDGETS ------------------------------------------------

# Website Home Page 
@app.route('/')
def home():
    return render_template("home.html")

def insert_data():
    db = DB(get_db_conn())
    tableset = ["shapes", "elections"]
    try:
        for i in tableset:
            db.create_table(i)
    except:
        logging.info("Data Creation Failed")


# Utilities ------------------------------

# Default Hostname/address code for temporary testing purposes
# Logging settings for log debugging
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        help="Server hostname (default 127.0.0.1)",
        default="127.0.0.1"
    )
    parser.add_argument(
        "-p", "--port",
        help="Server port (default 5000)",
        default=5000,
        type=int
    )
    parser.add_argument(
        "-l", "--log",
        help="Set the log level (debug,info,warning,error)",
        default="warning",
        choices=['debug', 'info', 'warning', 'error']
    )

    # The format for our logger
    log_fmt = '%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    
    # Create the parser argument object
    args = parser.parse_args()
    if args.log == 'debug':
        logging.basicConfig(
            format=log_fmt, level=logging.DEBUG)
        logging.debug("Logging level set to debug")
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.DEBUG)
    elif args.log == 'info':
        logging.basicConfig(
            format=log_fmt, level=logging.INFO)
        logging.info("Logging level set to info")
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.INFO)
    elif args.log == 'warning':
        logging.basicConfig(
            format=log_fmt, level=logging.WARNING)
        logging.warning("Logging level set to warning")
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.WARNING)
    elif args.log == 'error':
        logging.basicConfig(
            format=log_fmt, level=logging.ERROR)
        logging.error("Logging level set to error")
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    # Store the address for the web app
    app.config['addr'] = "http://%s:%s" % (args.host, args.port)

    logging.info("Starting Up!")
    app.run(host=args.host, port=args.port, threaded=False)
