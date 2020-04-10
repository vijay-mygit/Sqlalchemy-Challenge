import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine,reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"WELCOME TO THE CLIMATE APP HOMEPAGE<br/>"
        f"-----------------------------------------------<br/>"
        f"Available Routes:<br/>"
        f"-----------------------------------------------<br/>"
        f"Api to return the precipitation values for all dates.<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"-----------------------------------------------<br/>"
        f"Api for the list of stations from the dataset.<br/>"
        f"/api/v1.0/stations<br/>"
        f"-----------------------------------------------<br/>"
        f"Dates and Temperature observations of the most active station for the last year of data.<br/>"
        f"/api/v1.0/tobs<br/>"
        f"-----------------------------------------------<br/>"
        f" JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    all_prcp = []
    for date,prcp in results:
        measurement_dict = {}
        measurement_dict["date"] = date
        measurement_dict["prcp"] = prcp
        all_prcp.append(measurement_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    results = session.query(Station.station,Station.name).all()
    session.close()
    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(Station.station,Station.name,Measurement.date,Measurement.tobs).\
        filter(Measurement.date >='2016-08-23').\
        filter(Station.station =='USC00519281').all()
    session.close()
    all_tobs = []
    for station,name,date,tobs in results:
        measurement_dict = {}
        measurement_dict["name"] = name
        measurement_dict["station"] = station
        measurement_dict["date"] = date
        measurement_dict["tobs"] = tobs
        all_tobs.append(measurement_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/start_date")
def start():
    return(f"Please enter any date beween 2010-01-01 to 2017-08-23 in the place of start_date to obtain the Minimum, Average and Maximum Temperature values")
        
@app.route("/api/v1.0/<start_date>")
def value(start_date):
    session = Session(engine)
    start_date = dt.datetime.strptime(start_date,'%Y-%m-%d').date()
    first_date = dt.datetime.strptime('2010-01-01','%Y-%m-%d').date()
    last_date = dt.datetime.strptime('2017-08-23','%Y-%m-%d').date()
    sel = [Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    value = session.query(*sel).filter(Measurement.date >= start_date).group_by(Measurement.date).all()
    session.close()    
      

    if start_date > last_date or start_date < first_date:
        return jsonify({"error":f"Start date entered is out of range, please enter a date between 2010-01-01 to 2017-08-23"}),404 

    return jsonify(value)

@app.route("/api/v1.0/start_date/end_date")
def end():
    return(
        f"In place of start_date please enter any date between 2010-01-01 to 2017-08-23.<br/>"
        f"In place of end_date please enter any date between 2010-01-01 to 2017-08-23 until which u want to calculate the  Minimum, Average and Maximum temperature values"
    )

@app.route("/api/v1.0/<start_date>/<end_date>")
def value_2(start_date,end_date):
    session = Session(engine)
    start_date = dt.datetime.strptime(start_date,'%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end_date,'%Y-%m-%d').date()
    first_date = dt.datetime.strptime('2010-01-01','%Y-%m-%d').date()
    last_date = dt.datetime.strptime('2017-08-23','%Y-%m-%d').date()
    value_2 = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).group_by(Measurement.date).all()
    session.close()

    if start_date > last_date or start_date < first_date:
        return jsonify({"error":f"Start Date entered is out of range,please enter a date between 2010-01-01 to 2017-08-23"}),404 

    if end_date > last_date or end_date < start_date:
        return jsonify({"error":f"End Date entered is out of range,please enter a date between 2010-01-01 to 2017-08-23 greater than Start_date"}),404 
    
    return jsonify(value_2)
    
    
if __name__ == '__main__':
    app.run(debug=True)
