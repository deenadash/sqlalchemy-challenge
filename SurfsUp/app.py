import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with = engine)


# reflect the tables
Station = Base.classes.station
Measurement = Base.classes.measurement


# set the dates
lastdate = dt.date(2017, 8 ,23)
firstdate = dt.date (2010, 1 , 1)

#Calculation of date one year before the last date
date_1_year = lastdate - dt.timedelta(days=365)

#flask setup
app = Flask(__name__)

#flask routes
@app.routes("/")
def Homepage():
    return(
        f" Welcome to our climate app !<br/>"
        f" Availabe Paths:<br/>"
        f" /api/v1.0/precipitation<br/>"
        f" /api/v1.0/stations<br/>"
        f" /api/v1.0/tobs<br/>"
        f" /api/v1.0/Start_Date (YYYY-MM-DD)<br/>"
        f" /api/v1.0/Start_Date/End_Date (YYYY-MM-DD)"

    )

@app.route("/api/v1.0/precipitation")
def precipitaion():

    #creating session link from python to the DB
    session = Session(engine)

    #Query precipitation date
    outcome= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >+ date_1_year).all()

    session.close()

    #converting list into dictionary
    df_dist = {row[0]:row[1] for row in outcome}

    return jsonify(df_dist)

# JSON lists of station
@app.route("/api/v1.0/stations")
def stations():

    # Creating session link
    session = Session(engine)


    # Query all station data
    result_stn = session.query(Station.station).all()

    session.close()

    all_names= list(np.ravel(result_stn))

    return jsonify(all_names)

# JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():

    # create our session (link) from python to the DB
    session = Session(engine)

    # Query Measurement data

    temp_obs = session.query(Measurement.date, Measurement.tobs).\
               filter(Measurement.station == 'USC00519281').\
               filter(Measurement.date >= date_1_year).all()
    
    session.close()

    temp_obs_dist = { row[0]:row[1] for row in temp_obs}
    return jsonify(temp_obs_dist)


# Return min,max and average temperatures form the given start date to the end of the dataset
@app.route("/api/v1.0/<start>")
def startdate(start):
    try:
        inputstartdate =pd.to_datetime(start, format = '%Y-%m-%d').date()
        if ((inputstartdate>lastdate) |
           (inputstartdate<firstdate)):
           return jsonify({"error": f"Date {start} are beyond the range of dataset."}), 404
        else:
            session = Session(engine)

            sel = [func.min(Measurement.tobs),
                   func.avg(Measurement.tobs),
                   func.max(Measurement.tobs)]
            
            temp_obs = session.query(*sel).filter(Measurement.date >= inputstartdate).all()

            session.close()
    
            temp_obs_list = list(np.ravel(temp_obs))

            temp_obs_dict = {'min' : temp_obs_list[0],
                             'avg' : temp_obs_list[1],
                             'max' : temp_obs_list[2]}
            return jsonify(temp_obs_dict)
        
    except:
        return jsonify({ "error": f"The start date {start} not found or wrong formate."}), 404
    
# Returns the min, max and average temperatures calculated from the given date to given end date.
@app.route("/api/v1.0/<start>/<end>")
def firstlastdate(start,end):
    #using try and except to find the error 
    try:
        inputfirtdate = pd.to_datetime(start, format='%Y-%m-%d').date()
        inputlastdate = pd.to_datetime(end, format='%Y-%m-%d').date()
        if ((inputfirtdate>lastdate) |
         (inputfirtdate < firstdate)):
         return jsonify({"error" : f'Date {start} is beyond the range in provided dataset'}), 404
        elif ((inputlastdate > lastdate) |
         (inputlastdate < firstdate)):
         return jsonify({"error" : f'Date {end} is beyond the range in provided dataset'}), 404
        elif (inputlastdate < inputfirtdate):
         return jsonify ({"error" : f'End date {end} is before the start date {start}'}), 404
        else:
         session = Session(engine)

        sel = [func.min(Measurement.tobs),
               func.avg(Measurement.tobs),
               func.max(Measurement.tobs)]
        
        temp_obs = session.query(*sel).\
                  filter(Measurement.date >=inputfirtdate).\
                  filter(Measurement <= inputlastdate).all()
        
        session.close()

        #result into a normal list
        temp_obs_list = list(np.ravel(temp_obs))

        temmp_obs_dict = {"min": temp_obs_list[0],
                          "avg": temp_obs_list[1],
                          "max": temp_obs_list[2]}
        return jsonify(temmp_obs_dict)
    
    except:
     return jsonify({"error": f"Unable to track start date {start} or worng format"}), 404

if __name__ =='__main__':
   app.run(debug=True)
         



