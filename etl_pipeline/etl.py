#!/usr/bin/python3

# Task 1a
"""
Problem Statement:
1. Download files from the webpage:
    http://pgcb.gov.bd/site/page/0dd38e19-7c70-4582-95ba-078fccb609a8/-
2. When executed for the first time, the program should download files from the first page only
3. In subsequent execution, the program should download the newly added files
3. Schedule the script to run daily i.e. every 24 hours
4. After downloading the excel (.xls/.xlsm) file, clean the data that must satisfy following criteria:
    a. Data should be extracted from the excel sheet named “Forecast”
    b. Find and remove aggregated data such as Total or Area Total
    c. Show only individual features and the observations
    d. Store the data in Database or CSV files

Author  : Abdullah Reza
Date    : 20/01/2021
"""

# Libraries to extract files
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import json
import wget

# Libraries to transform data
import numpy as np
import pandas as pd

# Libraries to load data
import sqlite3
from sqlite3 import Error

# Initialization & constants
TARGET_URL = "http://pgcb.gov.bd/site/page/0dd38e19-7c70-4582-95ba-078fccb609a8/-"
DOWNLOAD_DIR = "../excel_files"
LOG_PATH = "../.log/state.json"
DB_DIR = "../database/powergen.db"
PGCB_ACTIVITY_TABLE = "pgcb_power_gen"

# Function to get file URLs
def extract_files(page_url, last_url):
    """
    This function gets the list of links for the files that are needed to be 
    downloaded from a webpage.
    :param page_url: webpage url (string)
    :param last_url: list of file URLs from previous run (string) 
    :return new_url: list of links of downloadable files (string)
    :return msg: function completion message
    """

    # Current URL list
    new_url = []
    # Function completion message
    msg = ""
    
    try:
        # Retrieve webpage HTML code
        response = requests.get(page_url)
        response.raise_for_status()
        
        # Parse the webpage HTML code
        soup = BeautifulSoup(response.content, "html.parser")
        
        # The downloadable files are inside iframe tag and the can be identified by report_by_category
        for frame in soup.find_all("iframe"):
            if "report_by_category" in frame["src"]:
                repository = frame["src"]
                
        # Retrieve repository HTML code
        response = requests.get(repository)
        response.raise_for_status()

        # Parse the HTML code
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Iterate through all the href to find relevant data (.xls/.xlsm)
        for link in soup.find_all("a", target = "_blank"):
            url = link.get("href")
            url = url.strip()
            new_url.append(url)

        # Check if last_url is empty
        if not last_url:
            # Download files
            for url in new_url:
                try:
                    print("\ndownloading:", url)
                    wget.download(url, DOWNLOAD_DIR)
                    last_url.append(url)
                except Exception as e:
                    print(e)
        else:
            # Find new files
            new_url = list(set(new_url) - set(last_url))
            for url in new_url:
                try:
                    print("\ndownloading:", url)
                    wget.download(url, DOWNLOAD_DIR)
                    last_url.insert(0, url)
                    last_url.pop()    
                except Exception as e:
                    print(e)
        
        # return the url_list and completion message
        new_url = last_url
        msg = "Success: File URLs retrieved."
        return new_url, msg
    except requests.exceptions.RequestException as e:
        print(e)
        msg = str(e)
        new_url = []
        return msg
    finally:
        return new_url, msg

# Function to transform data
def transform_data(path):
    """
    This function reads data from excel file and transform data by cleaning the 
    data, removing aggregated information such as area total and Total etc.
    :param path: path of the excel file (string)
    :return df: pandas dataframe
    """

    # Read file
    df = pd.read_excel(path, sheet_name = "Forecast")

    # Rename columns for easier handling
    df.columns = range(df.shape[1])
    # Reset row indices
    df.reset_index(drop = True, inplace = True)

    # Extract date
    date = df.where(df == "Date (day):").dropna(how="all").dropna(axis=1)
    date_row = date.index[0]
    date_columns = date.columns[0] + 1
    date = df.iat[date_row, date_columns]
    date = date.strftime("%m/%d/%Y")
    print("Transforming report on {}".format(date))

    # Slice dataframe to exclude redundant information i.e. aggregated information
    # Find start_row: 3 row below "Name of the Power Station"
    # Find start_col: Column of "Name of the Power Station"
    # Find last_row: Exclude all information below "Total"  
    power_station = df.where(df == "Name of the Power Station").dropna(how="all").dropna(axis=1)
    start_row = power_station.index[0] + 3
    start_col = power_station.columns[0]
    # total = df.where(df == "Total").dropna(how="all").dropna(axis=1)
    # last_row = total.index[0]
    last_row = -42
    df = df.iloc[start_row:last_row, start_col:]

    # Drop column 3 & column 16 which are adjacent column for power_station_name and
    # maintenance_remark respectively
    df.drop(columns = [3, 16], inplace = True)
    # Column header
    header = ["power_station_name", "fuel_type", "producer", "install_capacity", "total_capacity", "current_capacity",
            "prev_day_power_gen_peak", "prev_ev_power_gen_peak", "current_day_forecast_peak", "current_ev_forecast_peak",
            "gen_short_fuel", "gen_short_plant_issue", "maintenance_remark", "start_up_date"]
    # Rename column headers
    df.columns = header

    # Remove rows with aggregated information such as "area Total" or "Total"
    df = df[~df.power_station_name.str.contains("Total")]

    # Change data types for the numerical columns
    df = df.astype({"power_station_name" : "str",
                    "fuel_type" : "str",
                    "producer" : "str",
                    "install_capacity" : "str",
                    "total_capacity" : "float",
                    "current_capacity" : "float",
                    "prev_day_power_gen_peak" : "float",
                    "prev_ev_power_gen_peak" : "float",
                    "current_day_forecast_peak" : "float",
                    "current_ev_forecast_peak" : "float",
                    "gen_short_fuel" : "float",
                    "gen_short_plant_issue" : "float",
                    "maintenance_remark" : "str",
                    "start_up_date" : "str"})
    
    # Remove unnecessary whitespaces
    for column in df.columns:
        if df[column].dtype != np.number:
            df[column] = [" ".join(name.split()) for name in df[column].str.strip()]
            
    # Insert date column at the beginning of the dataframe
    df.insert(loc = 0, column = "report_date", value = date)
    
    return df

# Insert dataframe values to table
def load_data(table_name, db_name, df):
    """
    Load pandas dataframe and insert the data to the table
    :param table_name: table name in the database to insert the data into
    :param csv_file: path of the csv file to process
    :return: None
    """

    conn = connect_to_db(db_name)

    if conn is not None:
        c = conn.cursor()

        # Create table if it is not exist
        c.execute("CREATE TABLE IF NOT EXISTS " + table_name +
                  "(report_date               TEXT,"
                  "power_station_name         TEXT,"
                  "fuel_type                  TEXT,"
                  "producer                   TEXT,"
                  "install_capacity           TEXT,"
                  "total_capacity             REAL,"
                  "current_capacity           REAL,"
                  "prev_day_power_gen_peak    REAL,"
                  "prev_ev_power_gen_peak     REAL,"
                  "current_day_forecast_peak  REAL,"
                  "current_ev_forecast_peak   REAL,"
                  "gen_short_fuel             REAL,"
                  "gen_short_plant_issue      REAL,"
                  "maintenance_remark         TEXT,"
                  "start_up_date              TEXT)")

        df.columns = get_column_names_from_db_table(c, table_name)

        df.to_sql(name = table_name, con = conn, if_exists = "append", index = False)

        conn.close()
        print("SQL insert process finished")
    else:
        print("Connection to database failed")
        
# Connect to DB
def connect_to_db(db_file):
    """
    Connect to an SQlite database, if db file does not exist it will be created
    :param db_file: absolute or relative path of db file
    :return: sqlite3 connection
    """
    sqlite3_conn = None

    try:
        sqlite3_conn = sqlite3.connect(db_file)
        return sqlite3_conn

    except Error as err:
        print(err)

        if sqlite3_conn is not None:
            sqlite3_conn.close()

# Get the name of the columns of the table
def get_column_names_from_db_table(sql_cursor, table_name):
    """
    Scrape the column names from a database table to a list
    :param sql_cursor: sqlite cursor
    :param table_name: table name to get the column names from
    :return: a list with table column names
    """

    table_column_names = "PRAGMA table_info(" + table_name + ");"
    sql_cursor.execute(table_column_names)
    table_column_names = sql_cursor.fetchall()

    column_names = list()

    for name in table_column_names:
        column_names.append(name[1])

    return column_names

# Main Function
if __name__ == "__main__":
    # Check the status of the download operation
    if Path(LOG_PATH).exists():
        with open(LOG_PATH, "r") as file:
            last_status = json.load(file)
            last_url = last_status["last_url"]
    else:
        last_url = []
        all_files = []
    
    # Get the list of URLs for CSV files
    new_url, message = extract_files(TARGET_URL, last_url)
    
    # Transform and load data to local database
    for filename in Path(DOWNLOAD_DIR).glob("*.xlsm"):
        # Transform data
        if filename.stem in all_files:
            print("Data already exists in DB")
        else:
            df = transform_data(filename)
            load_data(PGCB_ACTIVITY_TABLE, DB_DIR, df)
            all_files.append(filename.stem)
            
    # Status of the download operation
    log = {
        "last_operation" : datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "last_url" : new_url,
        "all_files" : all_files,
        "completion_status" : message
    }
    
    # Create state.json for troubleshooting
    with open(LOG_PATH, "w") as status_file:
        json.dump(log, status_file, indent = 4)