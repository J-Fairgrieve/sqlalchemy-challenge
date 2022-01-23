import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<b>Available Routes:</b><br>"
        f"1. <a href=\"/api/v1.0/precipitation\">Previous year's precipitation data</a>: (/api/v1.0/precipitation)<br/>"
        f"2. <a href=\"/api/v1.0/stations\">List of all stations</a>: (/api/v1.0/stations)<br/>"
        f"3. <a href=\"/api/v1.0/tobs\">Previous year's temperature observations at the most active station</a>: (/api/v1.0/tobs)<br/>"
        f"4. Min, Average & Max Temperatures for Date Range: (/api/v1.0/trip/[start date]/[end date])<br><br>"
        f"<b>Dates provided must be in yyyy-mm-dd format, if no end-date is provided, the trip api calculates stats through 23/08/2017</b><br>" 
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """List all precipitation data for the previous year"""
    # Query precipitation data for previous year 
    
    start = '2016-08-23'
    sel = [measurement.date, 
        func.sum(measurement.prcp)]
    precipitation = session.query(*sel).\
            filter(measurement.date >= start).\
            group_by(measurement.date).\
            order_by(measurement.date).all()
   
    session.close()

    # Output precipitation data for previous year
    dates = []
    totals = []

    for date, dailytotal in precipitation:
        dates.append(date)
        totals.append(dailytotal)
    
    precipitation_dict = dict(zip(dates, totals))

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Output list of all the active Weather stations in Hawaii"""
    # Output list of active weather stations in Hawaii
    sel = [measurement.station]
    active_stations = session.query(*sel).\
        group_by(measurement.station).all()
    session.close()

    list_of_stations = list(np.ravel(active_stations)) 
    return jsonify(list_of_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the last 12 months of temperature observation data for the most active station
    start_date = '2016-08-23'
    sel = [measurement.date, 
        measurement.tobs]
    station_temps = session.query(*sel).\
            filter(measurement.date >= start_date, measurement.station == 'USC00519281').\
            group_by(measurement.date).\
            order_by(measurement.date).all()

    session.close()

    # Return a dictionary with the date as key and the daily temperature observation as value
    dates = []
    temps = []

    for date, observation in station_temps:
        dates.append(date)
        temps.append(observation)
    
    most_active_tobs_dict = dict(zip(dates, temps))

    return jsonify(most_active_tobs_dict)

@app.route("/api/v1.0/trip/<start_date>")
def trip1(start_date, end_date='2017-08-23'):
    # Calculate minimum, average and maximum temperatures for the range of dates starting with start date.
    # If no end date is provided, the function defaults to 2017-08-23.

    session = Session(engine)
    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    # If the query returned non-null values return the results,
    # otherwise return an error message
    if trip_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"error": f"Date {start_date} not found or not formatted as YYYY-MM-DD."}), 404
  
@app.route("/api/v1.0/trip/<start_date>/<end_date>")
def trip2(start_date, end_date='2017-08-23'):
    # Calculate minimum, average and maximum temperatures for the range of dates starting with start date.
    # If no valid end date is provided, the function defaults to 2017-08-23.

    session = Session(engine)
    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    # If the query returned non-null values return the results,
    # otherwise return an error message
    if trip_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"error": f"Date(s) not found, invalid date range or dates not formatted correctly."}), 404
  

if __name__ == '__main__':
    app.run(debug=True)
