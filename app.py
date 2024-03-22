# Design Climate App - Flask
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from pathlib import Path

##################################################
# Database Setup
##################################################
hawai_database_path = Path("../Resources/hawaii.sqlite")
engine = create_engine(f"sqlite:///{hawai_database_path}")
conn = engine.connect()
Base = automap_base() 
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

##################################################
# Flask Setup
##################################################
app = Flask(__name__)

# Homepage route to list all available routes
@app.route('/')
def home():
    routes = {
        "routes": [
            "/",
            "/api/v1.0/precipitation",
            "/api/v1.0/stations",
            "/api/v1.0/tobs",
            "/api/v1.0/<start>",
            "/api/v1.0/<start>/<end>"
        ]
    }
    return jsonify(routes)

# Return a JSON list of stations from the dataset
@app.route('/api/v1.0/stations')
def stations():
    results = session.query(Station.station).all()
    stations_list = [result for result, in results]
    return jsonify(stations_list)

# Define a Flask route handler function - Precipitation
@app.route('/api/v1.0/precipitation')
def precipitation():
    one_year_ago = datetime.today() - timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

# Return a JSON list of temperature observations
@app.route('/api/v1.0/tobs')
def tobs():
    most_active_station_id = "USC00519281"
    one_year_ago = datetime.today() - timedelta(days=365)
    
    tobs_data = session.query(Measurement.tobs)\
                .filter(Measurement.station == most_active_station_id)\
                .filter(Measurement.date >= one_year_ago)\
                .all()
    
    return jsonify({'temperature_observations': [tobs[0] for tobs in tobs_data]})

# Define a Flask route handler function for /api/v1.0/<start>
@app.route('/api/v1.0/<start>')
def temperature_start(start):
    temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                      .filter(Measurement.date >= start)\
                      .all()
    
    tmin, tavg, tmax = temperature_data[0]
    
    return jsonify({'TMIN': tmin, 'TAVG': tavg, 'TMAX': tmax})

# Define a Flask route handler function for /api/v1.0/<start>/<end>
@app.route('/api/v1.0/<start>/<end>')
def temperature_start_end(start, end):
    temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                      .filter(Measurement.date >= start)\
                      .filter(Measurement.date <= end)\
                      .all()
    
    tmin, tavg, tmax = temperature_data[0]
    
    return jsonify({'TMIN': tmin, 'TAVG': tavg, 'TMAX': tmax})

# Join the station and measurement tables to get combined data
@app.route('/api/v1.0/data')
def get_data():
    query_result = session.query(Station, Measurement).filter(Station.station == Measurement.station).all()
    
    data = []
    for station, measurement in query_result:
        data.append({
            'station_id': station.station,
            'station_name': station.name,
            'measurement_date': measurement.date,
            'temperature': measurement.tobs  # Corrected attribute name to match your model
        })
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)

 


