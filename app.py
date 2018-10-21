
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import datetime as dt


from flask import Flask, jsonify

import os
import numpy as np
file_path = os.path.join("Resources", "hawaii.sqlite")

connection_string = (f'sqlite:///{file_path}')

engine = create_engine(connection_string)

Base = automap_base()
Base.prepare(engine, reflect = True)

Station = Base.classes.stations
Measurement = Base.classes.measurements

session = Session(engine)


app = Flask(__name__)

startDate = dt.date(2016,11,21)
endDate = dt.date(2016,11,30)
lastDate = dt.date(2017, 8, 23)
yearAgo = dt.date(2017, 8, 23) - dt.timedelta(days=365)






# http://localhost:5000/
@app.route("/")
def home():
        "This is the homepage"
        return(
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/temp/start<br/>"
            f"/api/v1.0/temp/start/end"
        )

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset """
    results = session.query(Station.station).all()
    station_list = []
    for item in results:
        station_list.append(item[0])
    
    return jsonify(station_list)


@app.route("/api/v1.0/precipitation")
def precipitation():
    lastYearQuery = (session
        .query(Measurement.date, Measurement.tobs)
        .filter(Measurement.date>yearAgo)
        .filter(Measurement.date<=lastDate)
        .all()
    )
    lastYearDict = {}
    for row in lastYearQuery:
        lastYearDict[row[0]] = row[1]
    return(
        jsonify(lastYearDict)
    )





@app.route("/api/v1.0/tobs")
def tobs():
    tempQuery = (session
        .query(Measurement.tobs)
        .filter(Measurement.date>yearAgo)
        .filter(Measurement.date<=lastDate)
        .all()
    )
    tempList = []
    for row in tempQuery:
        tempList.append(row[0])

    return(jsonify(tempList))



@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def temp_stats(start=2018, end=None):
    print(f"this is a the start date: {start} <br/>"
          f"this is the end date: {end}"
          f"format should be 'yyyy-mm-dd'"
          )

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

        # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)