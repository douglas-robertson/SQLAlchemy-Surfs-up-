import numpy as np
import sqlalchemy
import datetime as dt
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
app = Flask(__name__)

#Setup
#Engine/Relect
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect existing & tables
Base = automap_base()
Base.prepare(engine, reflect=True)

#view all of the classes that automap found
Base.classes.keys()

Station = Base.classes.station
Measurement = Base.classes.measurement




#routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"All available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #create session
    session = Session(engine)

    #date range query
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016,8,23').order_by(
            Measurement.date).all()
    session.close()

    #dict convert
    date_prcp = []
    for date, prcp in results:
        date_prcp_dict = {}
        date_prcp_dict['date'] = date
        date_prcp_dict['prcp'] = prcp
        date_prcp.append(date_prcp_dict)

    return jsonify(date_prcp)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    #stns query
    results = session.query(Station.station, Station.name).all()

    session.close()

    #dict convert
    stations_name = []
    for station, name in results:
        stations_name_dict = {}
        stations_name_dict['station'] = station
        stations_name_dict['name'] = name
        stations_name.append(stations_name_dict)
    
    return jsonify(stations_name)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    #stations query
    highest_tobs_station=session.query(Measurement.station,func.max(Measurement.tobs)).first()
    
    last_observation=session.query(Measurement.date).\
    filter(Measurement.station==highest_tobs_station[0]).\
    order_by(Measurement.date.desc()).first()
    
    year_ago=dt.datetime(2017,8,23)-dt.timedelta(days=365)
    
    #12m query
    tobs_total=session.query(Measurement.station,Measurement.tobs).\
    filter(Measurement.station == highest_tobs_station[0]).order_by(Measurement.date).all()

    #dict convert
    tobs_temp_active = []
    for station, tobs in tobs_total:
        tobs_temp_active_dict = {}
        tobs_temp_active_dict['station'] = station
        tobs_temp_active_dict['tobs'] = tobs
        tobs_temp_active.append(tobs_temp_active_dict)
    session.close()


    return jsonify(tobs_temp_active)

@app.route("/api/v1.0/<start>")
def stats(start):
    session = Session(engine)
    
    #min max query w date filter
    results = session.query(func.min(Measurement.tobs).label('min_temp'), func.max(Measurement.tobs).label('max_temp'), func.avg(Measurement.tobs).label('avg_temp'))\
        .filter(Measurement.date >= start).all()
    session.close()
    
    #dict convert
    stats_tobs = []
    for r in results:
        tobs_dict = {}
        tobs_dict['min_temp'] = r.min_temp
        tobs_dict['max_temp'] = r.max_temp
        tobs_dict['avg_temp'] = r.avg_temp

        stats_tobs.append(tobs_dict)

    return jsonify(f"Start date:{start}",stats_tobs)
@app.route("/api/v1.0/<start>/<end>")
def stats_end(start,end):

    session = Session(engine)
    
    #min max query with date range
    results = session.query(func.min(Measurement.tobs).label('min_temp'), func.max(Measurement.tobs).label('max_temp'), func.avg(Measurement.tobs).label('avg_temp'))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date<= end).all()
    session.close()
    
    #dict convert
    stats_tobs = []
    for r in results:
        tobs_dict = {}
        tobs_dict['min_temp'] = r.min_temp
        tobs_dict['max_temp'] = r.max_temp
        tobs_dict['avg_temp'] = r.avg_temp

        stats_tobs.append(tobs_dict)

    return jsonify(f"Start date:{start}",f"End date:{end}",stats_tobs)


if __name__ == '__main__':
    app.run(debug=True)