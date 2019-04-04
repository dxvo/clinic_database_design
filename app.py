import os
import pandas as pd
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


#################################################
# Database Setup
#################################################

app.config["CLEARDB_DATABASE_URL"] =  ""
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(db.engine, reflect=True)

# # Save references to each table
# Samples_Metadata = Base.classes.sample_metadata
# Samples = Base.classes.samples

@app.route('/')
@app.route('/homepage/')
def homepage():
    return render_template('index.html')

@app.route('/register/')
def registerpage():
    return render_template('register.html')

@app.route('/patient_reg/')
def patient_reg():
    return render_template('patient_reg.html')

if __name__ == "__main__":
    app.run(debug=True)