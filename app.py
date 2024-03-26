import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///../hawaii.sqlite")
conn = engine.connect()

Base = automap_base()

# reflect the tables
# Base.prepare(autoload_with=engine)

# Save reference to the table
# Measurement = Base.classes.measurement
# Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Define the homepage route
@app.route("/")
def home():
    return """
    <h1>Welcome to the Climate App!</h1>
    <h2>Available Routes:</h2>
    <ul>
        <li><a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></li>
        <li><a href="/api/v1.0/stations">/api/v1.0/stations</a></li>
        <li><a href="/api/v1.0/tobs">/api/v1.0/tobs</a></li>
        <li><a href="/api/v1.0/start">/api/v1.0/start</a></li>
        <li><a href="/api/v1.0/start/end">/api/v1.0/start/end</a></li>
    </ul>
    """

# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    try:
        session = Session(engine)
        results = session.query(Station.station).all()
        stations_list = [result for result, in results]
        return jsonify(stations_list)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        session.close()

# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    try:
        session = Session(engine)
        one_year_ago = datetime.today() - timedelta(days=365)
        results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
        precipitation_data = {date: prcp for date, prcp in results}
        return jsonify(precipitation_data)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        session.close()

# Define the temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    try:
        session = Session(engine)
        most_active_station_id = "USC00519281"
        one_year_ago = datetime.today() - timedelta(days=365)
        tobs_data = session.query(Measurement.tobs).\
            filter(Measurement.station == most_active_station_id).\
            filter(Measurement.date >= one_year_ago).all()
        return jsonify({'temperature_observations': [tobs[0] for tobs in tobs_data]})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        session.close()

# Define the start route
@app.route("/api/v1.0/<start>")
def start(start):
    try:
        session = Session(engine)
        temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        tmin, tavg, tmax = temperature_data[0]
        return jsonify({'TMIN': tmin, 'TAVG': tavg, 'TMAX': tmax})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        session.close()

# Define the start-end route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    try:
        session = Session(engine)
        temperature_data = session.query(func.min(Measurement.measurement), func.avg(Measurement.measurement), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        tmin, tavg, tmax = temperature_data[0]
        return jsonify({'TMIN': tmin, 'TAVG': tavg, 'TMAX': tmax})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        session.close()

# After defining routes, but before if __name__ == '__main__':
print(Base.classes.keys())

# Run the app
if __name__ == '__main__':
    app.run(debug=True)