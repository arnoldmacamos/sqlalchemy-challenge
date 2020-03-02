from flask import Flask, jsonify
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime

import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func, text



engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


#Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")

    return (
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    tMaxDate = session.query(func.max(Measurement.date) ).first()
    maxDate =  datetime.strptime(tMaxDate[0], '%Y-%m-%d').date() 
    dt1yrago =  (maxDate - pd.DateOffset(months=12)).date()

    # Perform a query to retrieve the data and precipitation scores
    #selCols = [Measurement.id, Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs]
    selCols = [Measurement.date, Measurement.prcp]
    resultData =  session.query(*selCols).filter(Measurement.date >= dt1yrago).all()

    # Save the query results as a Pandas DataFrame and set the index to the date column
    df_prcp = pd.DataFrame(resultData)
    df_prcp.set_index('date')

    # Sort the dataframe by date
    df_prcp.sort_values(by='date', ascending=True)
    dict_prcp  = df_prcp.replace({np.nan: None}).to_dict('records')    
    return jsonify(dict_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    #selCols2 = [Measurement.station]
    resultData2 =  session.query(Station.station, Station.name)
    df_stn = pd.DataFrame(resultData2,columns=['station','name'])
    #df_stn = df_stn.sort_values(by='count', ascending=False)
    #df_stn.set_index('station')
    dict_stn = df_stn.replace({np.nan: None}).to_dict('records')    
    return jsonify(dict_stn)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    tMaxDate = session.query(func.max(Measurement.date) ).first()
    maxDate =  datetime.strptime(tMaxDate[0], '%Y-%m-%d').date() 
    dt1yrago =  (maxDate - pd.DateOffset(months=12)).date()

    resultData4 =  session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= dt1yrago)
    df_tobs = pd.DataFrame(resultData4, columns=['date','tob'])
    dict_tobs  = df_tobs.replace({np.nan: None}).to_dict('records')    
    return jsonify(dict_tobs)

@app.route("/api/v1.0/<start>")
def get_temp_summary_by_startdate(start):
    start = datetime.strptime(start, "%Y-%m-%d").date()
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    dict_temp = { "TMIN": result[0][0] , 'TAVE': result[0][1], 'TMAX' : result[0][2]}
    return jsonify(dict_temp)

@app.route("/api/v1.0/<start>/<end>")
def get_temp_summary_by_start_end_date(start,end):
    start = datetime.strptime(start, "%Y-%m-%d").date()
    end = datetime.strptime(end, "%Y-%m-%d").date()
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    dict_temp = { "TMIN": result[0][0] , 'TAVE': result[0][1], 'TMAX' : result[0][2]}
    return jsonify(dict_temp)

# 4. Define what to do when a user hits the /about route
@app.route("/about")
def about():
    print("Server received request for 'About' page...")
    return "Welcome to my 'About' page!"


if __name__ == "__main__":
    app.run(debug=True)
