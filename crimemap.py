#from dbhelper import DBHelper
from flask import Flask
from flask import render_template
from flask import request
import json
import datetime
import dateparser
import string

import dbconfig
if dbconfig.test:
    from mockdbhelper import MockDBHelper as DBHelper
else:
    from dbhelper import DBHelper

categories = ['mugging', 'break-in']

app = Flask(__name__)
DB = DBHelper()

@app.route("/")
def home(error_message=None):
    crimes = DB.get_all_crimes()
    crimes = json.dumps(crimes)
    return render_template("home.html", crimes=crimes, categories=categories,
            error_message=error_message)
    """
    try:
        data = DB.get_all_inputs()
    except Exception as e:
        print (e) 
        data = None
    return render_template("home.html", data=data)
    """

@app.route("/add", methods=["POST"])
def add():
    try:
        data = request.form.get("userinput")
        DB.add_input(data)
    except Exception as e: 
        print (e) 
    return home()

@app.route("/clear")
def clear():
    try:
        DB.clear_all()
    except Exception as e:
        print (e) 
    return home()

@app.route("/submitcrime", methods=['POST'])
def submitcrime():
    category = request.form.get("category")
    if category not in categories:
        return home()
    date = format_date(request.form.get("date"))
    if not date:
        return home("Invalid date. PLease use yyy-mm-dd format")
    try:
        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
    except ValueError:
        return home()

    description = sanitize_string(request.form.get("description"))

    DB.add_crime(category, date, latitude, longitude, description)

    return home()

def format_date(userdate):
    date = dateparser.parse(userdate)
    try:
        return datetime.datetime.strftime(date, "%Y-%m-%d")
    except TypeError:
        return None

def sanitize_string(userinput):
    whitelist = string.ascii_letters + string.digits + " !?$.,;:-'()&"
    a = filter(lambda x: x in whitelist, userinput)
    my_str = ""
    for i in a:
        my_str += i

    return my_str

if __name__ == '__main__':
    app.run(port=5000, debug=True)