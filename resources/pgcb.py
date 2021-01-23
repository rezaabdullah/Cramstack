# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 20:28:47 2021

@author: Reza
"""
"""
from flask import Blueprint, Response, request, render_template
from flask_restful import Resource
from sqlalchemy import create_engine
import pandas as pd

pgcb = Blueprint("pgcb", __name__)

# Initialize database and table
DB_DIR = "database/powergen.db"
TABLE_NAME = "pgcb_power_gen"

engine = create_engine("sqlite:///" + DB_DIR)
df = pd.read_sql_table(TABLE_NAME, engine)

# Homepage with welcome message
@pgcb.route("/")
def index():
    return Response(render_template("index.html"), status = 200)

# Show all data
@pgcb.route("/show_all")
def get_all():
    return Response(render_template("show_all.html", tables = [df.to_html(classes = "data")], titles = df.columns.values), status = 200)
"""

from flask import Response, render_template, request
from flask_restful import Resource
from sqlalchemy import create_engine, MetaData
import pandas as pd
import numpy as np
from resources.errors import InternalServerError, SchemaValidationError, DataNotExistsError, ThresholdError
from sqlalchemy.orm import sessionmaker
import re
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process


# Initialize database and table
DB_DIR = "database/powergen.db"
TABLE_NAME = "pgcb_power_gen"

# load data
engine = create_engine("sqlite:///" + DB_DIR)
#df = pd.read_sql_table(TABLE_NAME, engine) 

Session = sessionmaker(bind = engine)
session = Session()

# Function that converts tuple to string
def join_tuple_string(strings_tuple) -> str:
    return "".join(strings_tuple)

class PgcbHome(Resource):
    def get(self):
        return Response(render_template("index.html"), status = 200)

class Pgcb(Resource):
    def get(self):
        try:
            df = pd.read_sql_table(TABLE_NAME, engine)
            return Response(render_template("show_all.html", tables = [df.to_html(classes = "data")], titles = df.columns.values), status = 200)
        except Exception as e:
            raise InternalServerError
            
class PgcbFilter(Resource):
    def get(self):
        try:
            df = pd.read_sql_table(TABLE_NAME, engine)
            
            # Get request parameters as key value pair
            args = dict(request.args)
            # Use regex to replace the string for numerical operator
            # Allowable numerical operator:
            # ge: Greater than or equal to (>=)
            # gt: Greater than (>)
            # le: Less than or equal to (<=)
            # lt: Less than (<)
            # For MVP, basic regex operations are implemented
            for key in args:
                # Check if query parameters are numeric
                if df[key].dtypes == np.number:
                    # Check if numerical operator is in value and
                    # replace numerical operator with appropriate math operator
                    if re.search("(ge)", args[key]):
                        args[key] = re.sub("(ge)", " > ", args[key])
                    elif re.search("(gt)", args[key]):
                        args[key] = re.sub("(gt)", " >= ", args[key])
                    elif re.search("(le)", args[key]):
                        args[key] = re.sub("(le)", " < ", args[key])
                    elif re.search("(lt)", args[key]):
                        args[key] = re.sub("(lt)", " <= ", args[key])
                    else:
                        args[key] = " == " + args[key]
                else:
                    # If parameter is string, find the unique list from the associated string column
                    unique_list = df[key].unique().tolist()
                    query_param = args[key]
                    query_param, thres = query_param.split("_")
                    # Compare Strings
                    query_param = process.extract(query_param, unique_list, scorer = fuzz.token_sort_ratio)
                    query_param = [i for i in query_param if i[1] > int(thres)]
                    query_param = query_param[0][0]
                    args[key] = " == '" + query_param + "'"
                    
            # Converts args to list
            args = list(args.items())
            # Convert key-value tuples to string and join them
            result = list(map(join_tuple_string, args))
            statement = " and ".join(result)
            
            # Query data
            df = df.query(statement)
                            
            return Response(render_template("filter.html", tables = [df.to_html(classes = "data")], titles = df.columns.values), status = 200)
        except KeyError:
            raise KeyError
        except Exception as e:
            raise InternalServerError