from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime, timedelta

# Create engine and reflect the database
engine = create_engine("sqlite:///C:/Users/secar/OneDrive/Documents/Bootcamp/Starter_Code/Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Create session
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Define routes
@app.route("/")
def Welcome():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/start_date'>/api/v1.0/start_date</a><br/>"
        f"<a href='/api/v1.0/start_date/end_date'>/api/v1.0/start_date/end_date</a>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return JSON list of date and precipitation for the last year."""
    # Calculate the date 1 year ago from the last data point
    last_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = datetime.strptime(last_date, '%Y-%m-%d') - timedelta(days=365)
    
    # Query for the date and precipitation for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
              filter(Measurement.date >= one_year_ago).all()
    
    # Convert query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return JSON list of stations."""
    results = session.query(Station.station).all()
    stations_list = [station for station, in results]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return JSON list of temperature observations (tobs) for the most active station."""
    # Query for the most active station
    most_active_station = session.query(Measurement.station).\
                          group_by(Measurement.station).\
                          order_by(func.count().desc()).first()[0]
    # Calculate the date 1 year ago from the last data point
    last_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = datetime.strptime(last_date, '%Y-%m-%d') - timedelta(days=365)
    
    # Query for the date and temperature observations of the most active station for the last year
    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.station == most_active_station).\
              filter(Measurement.date >= one_year_ago).all()
    
    # Convert query results to a list of dictionaries
    tobs_data = [{date: tobs} for date, tobs in results]
    
    return jsonify(tobs_data)    

@app.route("/api/v1.0/<start>")
def start_stats(start):
    """Return JSON list of min, avg, and max temperatures from a start date to the end of the dataset."""
    # Query for temperature statistics
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()
    
    # Convert query results to a list of dictionaries
    temp_stats = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in results]
    
    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end_stats(start, end):
    """Return JSON list of min, avg, and max temperatures from a start date to an end date."""
    # Query for temperature statistics
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).\
              filter(Measurement.date <= end).all()
    
    # Convert query results to a list of dictionaries
    temp_stats = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in results]
    
    return jsonify(temp_stats)

    if __name__ == '__main__':
        app.run(debug=True)