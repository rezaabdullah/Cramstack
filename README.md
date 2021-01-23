# Cramstack Data Engineer Assignment

## Task 1a: ETL Job
### Overview
**Problem Statement:** Run an ETL Job in every 24 hours that extract data from a specific source, transform the data and load the data to local database.  
**Objective:**
1. Download power generation activity from: [Power Generation Company of Bangladesh Daily Activity Webpage](http://pgcb.gov.bd/site/page/0dd38e19-7c70-4582-95ba-078fccb609a8/-)
2. When first initialized, the script will download data from first page only. In subsequent execution, the script will automatically download **ONLY** the newly added files from the first page.
3. Schedule the script to run every 24 hours
4. Transform the data from the "Forecast" worksheet of the downloaded excel files
5. Find **Date** from the worksheet
6. Clean the data to remove aggregated information such as Total, Area Total etc.
7. Remove any redundant data
8. Add a **Date** column to the table
8. Store data in flat files or local database
9. Append the new data to local database

### ETL Logic
There are two possible routes that can be taken for ETL job:
1. **Route 1:** Extract i.e. download individual file, transform data and store it
2. **Route 2:** Extract files in **batch**, transform data and store it

To persist the data, data were stored in local **SQL database**

Since net connectivity is an external risk, route 2 was implemented in this script.

**Logic:**
1. **Extract**  
  i. Use `Beautiful Soup` library to extract the HTML code from the given webpage  
  ii. Identify and locate the `src` for the frame that shows daily report  
  iii. Use `Beautiful Soup` to extract the HTML code from the `src` link  
  iv. Find the `<a><\a>` with attribute `table = _blank`  
  v. Extract all the `href` link  
  vi. If the link does not exists in `state.json`, use `wget` library to download data  
2. **Transform**  
  i. Use `Pathlib` library to recursively extract all the filepath  
  ii. Use `Pandas` to create dataframe  
  iii. Extract `Date` from the relevant column  
  iv. Slice the dataframe until `Total`  
  v. Rename column headers  
  vi. Remove rows containing aggregated information i.e. `Total`  
  vii. Change the datatype of individual columns to their infered type i.e. `Numerical` or `String`  
  viii. Remove unnecessary whitespaces from `String` type columns  
  ix. Insert **Date** column at the beginning  
  x. Return Dataframe to load to local DB
3. **Load**  
  i. Use `sqllite3` library to create sqllite database  
  ii. If the table does not exist, create new table  
  iii. Retrieve the schema  
  iv. Coerce the data model with dataframe; meaning the columns data type in dataframe should match with table data types  
  v. Append dataframe into the database  

**Note:** In addition to ETL, a log file was created `state.json` to record logs of the previous day along with keep track of downloaded files.

### Project Structure
Cramstack  
|\_\_\_\_etl_pipeline  
&nbsp; &nbsp; &nbsp; &nbsp;|\_\_\_\_etl.py  
|\_\_\_\_database  
&nbsp; &nbsp; &nbsp; &nbsp;|\_\_\_\_powergen.db  
|\_\_\_\_excel_files  
&nbsp; &nbsp; &nbsp; &nbsp;|\_\_\_\_...excel files  
|\_\_\_\_.log
&nbsp; &nbsp; &nbsp; &nbsp;|\_\_\_\_state.json 

### Requirements
Following libraries are required
```python
requests
beautifulsoup
pathlib
wget
pandas
numpy
sqlite3
```
## Task 1b: Create an API
### Overview
**Problem Statement:** Create an API to access data from local database
**Objective:**
1. API should accept request and return data
2. No security features are required
3. Query Parameters:  
  i. Numerical Columns: Query parameters should be comparison operators such as:  
    * `gt`: Greater than  
    * `ge`: Greater than or equal to  
    * `lt`: Less than  
    * `le`: Less than or equal to  
    * `=` : Equal to  
  ii. String Column: Query parameters should be string to match and threshold. If the string to match is over the threshold then return the associated query  

### Project Structure
Cramstack  
|\_\_\_\_app.py  
|\_\_\_\_database  
&nbsp; &nbsp; &nbsp; &nbsp;|\_\_\_\_powergen.db  
|\_\_\_\_resources  
&nbsp; &nbsp; &nbsp; &nbsp;|\_\_\_\_errors.py  
&nbsp; &nbsp; &nbsp; &nbsp;|\_\_\_\_pgcb.py  
&nbsp; &nbsp; &nbsp; &nbsp;|\_\_\_\_routes.py  
|\_\_\_\_templates  
&nbsp; &nbsp; &nbsp; &nbsp;|\_\_\_\_filter.html  
&nbsp; &nbsp; &nbsp; &nbsp;|\_\_\_\_index.html  
&nbsp; &nbsp; &nbsp; &nbsp;|\_\_\_\_show_all.html  

### Requirements
```python
flask
flask_restful
sqlalchemy
pandas
numpy
re
fuzzywuzzy
```

### How to Use the API
1. In the Terminal (Linux/MacOS) or Command Prompt or Powershell (Windows) go to the project folder i.e. Cramstack
2. Enter `run app.py`
3. Open browser and in the address bar enter `http://localhost:5000` or `http://127.0.0.1:5000/`
4. To see all data, in the address bar enter `http://localhost:5000/show_all` or `http://127.0.0.1:5000/show_all`
5. To filter data, in the address bar enter `http://localhost:5000/filter?<query_parameter(s)>`
6. Multiple query parameters are allowed and must be separated by `&`

Allowable `<query parameter(s)>` are given below:
1. Numerical Queries:  
  i. `total_capacity`: e.g. `total_capacity=110` meaning `total_capacity` **equals** `110`
  ii. `current_capacity`: e.g. `current_capacity=gt110` meaning `current_capacity` **is greater than** 110  
  iii. `prev_day_power_gen_peak`: e.g. `prev_day_power_gen_peak=ge110` meaning `prev_day_power_gen_peak` **is greater than or equals** 110  
  iv. `prev_ev_power_gen_peak`: e.g. `prev_ev_power_gen_peak=lt110` meaning `prev_ev_power_gen_peak` **is less than** 110  
  v. `current_day_forecast_peak`: e.g. `current_day_forecast_peak=le110` meaning `current_day_forecast_peak` **is less than or equals** 100  
  vi. `current_ev_forecast_peak`: e.g. `current_ev_forecast_peak=110`  
  vii. `gen_short_fuel`: e.g. `gen_short_fuel=lt110`  
  viii. `gen_short_plant_issue`: e.g. `gen_short_plant_issue=ge110`  
2. String Queries:  
  i. `power_station_name`: e.g. `power_station_name=Bheramara_70` meaning `power_station_name` `Bheramara` should match with a threshold of at least `70`  
  ii. `fuel_type`: e.g. `fuel_type=gas_70`  
  iii. `producer`  
  iv. `install_capacity`  
  v. `return_date`  
  vi. `maintenance_remark`  
  vii. `start_up_date`

**Example:**
1. To filter data with `total_capacity` of 110 and `current_capacity` below 100: `http://localhost:5000/filter?total_capacity=100&current_capacity=lt100`
2. To filter data with `total_capacity` of over 500 and `power_station_name` matching with `Bheramara (HVDC)` wtih match threshold over 70: `http://localhost:5000/filter?total_capacity=gt500&power_station_name=Bheramara (HVDC)_70`

**Note:** In the above example, we see that multiple query parameters can be requested as long as they are separated by `&`.