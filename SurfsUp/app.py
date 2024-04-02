# Import necessary libraries
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt
from datetime import datetime, timedelta

# Database Setup
engine = create_engine("sqlite:///sqlalchemy-challenge/Resources/hawaii.sqlite")

# conn = engine.connect()

# Reflect the existing database tables into a new model
Base = automap_base()

# Reflect the tables from the database
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
##########################
# Flask Setup
app = Flask(__name__)
##########################


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
        <li><a href="/api/v1.0/start_date">/api/v1.0/start_date</a></li>
        <li><a href="/api/v1.0/start_date/end_date">/api/v1.0/start_date/end_date</a></li>
    </ul>
    """


@app.route("/api/v1.0/stations")
def stations():
    try:
        session = Session(engine)
        results = session.query(Station.station).all()
        stations_list = [{"Station": result} for result, in results]  # Include header "Station"
        return jsonify(stations_list)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        session.close()



# Define the precipation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a dictionary and return as JSON."""
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
                                 .filter(Measurement.date >= one_year_ago)\
                                 .all()
    session.close()
    
    # Create a list of dictionaries with headers
    precipitation_list = [{"Date": date, "Precipitation Value": prcp} for date, prcp in precipitation_data]
    
    return jsonify(precipitation_list)




# Define the temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    try:
        session = Session(engine)

        # Determine the most recent date in the dataset
        most_recent_date = session.query(func.max(Measurement.date)).scalar()
        most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')

        # Calculate the date one year ago from the most recent date
        one_year_ago = most_recent_date - timedelta(days=365)

        # Define the most active station ID
        most_active_station_id = 'USC00519281'

        # Query to retrieve temperature observations for the most active station
        tobs_data = session.query(Measurement.tobs)\
                           .filter(Measurement.station == most_active_station_id)\
                           .filter(Measurement.date >= one_year_ago)\
                           .filter(Measurement.date <= most_recent_date)\
                           .all()

        # Convert the query results to a list
        temperature_observations = [tobs[0] for tobs in tobs_data]

        return jsonify({'most_active_station': most_active_station_id, 'temperature_observations': temperature_observations})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        session.close()

# Define the start route
@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date."""
    session = Session(engine)
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                            .filter(Measurement.date >= start_date)\
                            .all()
        temp_stats_list = [{"Minimum Temperature": result[0], "Average Temperature": result[1], "Maximum Temperature": result[2]} for result in temp_stats]
        return jsonify(temp_stats_list)
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD format."}), 400
    finally:
        session.close()

# Define the start/end route
# Define the start/end route dynamically
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    try:
        session = Session(engine)
        temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        tmin, tavg, tmax = temperature_data[0]
        return jsonify({'TMIN': tmin, 'TAVG': tavg, 'TMAX': tmax})
    except Exception as e:
        return jsonify({"message": "An error occurred", "details": str(e)})
    finally:
        session.close()

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
