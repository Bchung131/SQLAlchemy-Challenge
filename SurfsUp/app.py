# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, text

import numpy as np
import pandas as pd
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome(): 
    return (
            f"Welcome to the Climate App Home Page! <br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitation <br/>"
            f"/api/v1.0/stations <br/>"
            f"/api/v1.0/tobs <br/>"
            f"/api/v1.0/<start> <br/>"
            f"/api/v1.0/<start>/<end> <br/>"
            f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"
            )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create  session from Python to the DB
    session = Session(engine)

    # Perform query for precipitation analysis results
    precipitation_results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.asc()).\
    filter(Measurement.date <= '2017-08-23').\
    filter(Measurement.date >= '2016-08-23').all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation_list
    precipitation_list = []
    for date, prcp in precipitation_results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation_list.append(precipitation_dict)
        
    return jsonify(precipitation_list)


@app.route("/api/v1.0/stations")
def stations():
    # Create  session from Python to the DB
    session = Session(engine)
    
    # Query all stations
    stations_list = session.query(Measurement.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(stations_list))
    
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    
    # Create  session from Python to the DB
    session = Session(engine)
    
    # Query most active station previous year data
    most_active_station = session.query(Measurement.date,Measurement.tobs).filter(Measurement.station == 'USC00519281').\
filter(Measurement.date <= '2017-08-23').\
filter(Measurement.date >= '2016-08-23').all()

    session.close()

    # Convert list of tuples into normal list
    active_station_list = list(np.ravel(most_active_station))
    
    return jsonify (active_station_list)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def date_stats(start=None, end=None):
    
# Find min, max and average temps from specific date   
    session = Session(engine)
    temp_sel_stats = [func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)]
    
    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        
        temps_query_result = session.query(*temp_sel_stats).\
            filter(Measurement.date >= start).all()
            
        session.close()
        
        temps = list(np.ravel(temps_query_result))
        return jsonify(temps)

    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    
    temps_query_result = session.query(*temp_sel_stats).\
        filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    
    session.close()
    
if __name__ == '__main__':
    app.run()