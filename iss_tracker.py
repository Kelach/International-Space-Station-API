from flask import Flask, request
from typing import List
from geopy.geocoders import Nominatim
from datetime import datetime
import time
import math
import requests
import logging

# Error logging
logging.basicConfig()

## GLOBAL VARIABLES
app = Flask(__name__)
DATA_URL = "https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.txt"
KMS_TO_MPH = 2236.936292  # 1 km/s : 2236 MPH
KM_TO_M = 0.6213711922    # 1 km : 0.6213 Miles
MEAN_EARTH_RADIUS_MAP = {"SI": 6371, "USCS": 3958.8}

## HELPER FUNCTIONS 
def load_data():
    '''
    Description
    -------
        Parses ISS data into a list of dictionaries using txt_to_dict().
    Args
    -------
        None    
    Returns
    --------
    List of dictionaries containing ISS state vectors
    '''
    # retrieve text data from ISS website
    txt = requests.get(DATA_URL).text
    # Initalize the keys of our data dictionaries
    keys = ["epoch", "X", "Y", "Z", "X_Dot", "Y_Dot", "Z_Dot"]
    # return list of dictionaries using txt_to_dict()
    data = txt_to_dict(txt, keys, "\r\n", " ", "COMMENT End sequence of events")

    # converting position and velocity vectors from string to float
    # for each item
    for item in data:
        # for each key of each item
        for key in keys:
            # if the key is position or velocity value, convert to float
            if key != "epoch":
                item[key] = float(item[key])
    return data

def get_data_info(txt:str, delimiter:str, stop:str, start:str="", info_type:str="dictionary"):
    '''
    Description
    -----------
        - Parses text data into a dictionary or list based on a starting and ending point and a delimiter 
    Parameters
    -----------
        - txt: string text to be parsed
        - delimiter: string pattern to be used to split each line in half (if dictionary, 
                    delimited should be the pattern seperating key-value pairs. I
                    f a list, the pattern should target any unwanted pre-fixed charactesr)
        - stop: ending pattern of target text
        - start: starting pattern of target text (empty string indicates start from beginning)
        - info_type: choose whether to parse the string text into a 'dictionary' or 'list' object

    Returns
    -----------
        - List/Dictionary of parsed text. If a list, it is a list of strings. 
            And the key-value pairs of the dictionaries are both strings.
    '''
    # initialize info data
    info = {} if info_type == "dictionary" else []
    
    # By default, we want to parse the start of a given txt parameter
    parse = start == ""

    # For each line in the text, skim until we 
    # reach the start of our target text, then
    # convert the data into a dictionary/list object
    for line in txt.splitlines():
        # Leave loop if we reach the end of our target text 
        if (line.strip() == stop.strip()):
            break
        # Begin parsing text if we've reached the 
        # start of our target text
        elif line.strip() == start.strip():
            parse = True 
            continue
        # Text parsing
        if line and parse:
            item = line.split(delimiter, 1)
            if info_type == "dictionary":
                info[item[0].strip()] = item[1].strip()
            elif info_type == "list":
                if item[1].strip():
                    info.append(item[1])
            else:
                raise ValueError("The given input_type is not supported. use 'dictionary' or 'list' only!")
    return info

def txt_to_dict(txt: str, keys: List[str], splitlines: str, splitline: str, start: str = "") -> List[dict]:
    '''
    Description
    -------
        Converts a given text into list of dictionaries where each dictionary
        was a originally a single line in the text file
    Args
    -------
        txt: Text to be parsed
        keys: list of keys to be paired with each dictionary
        splitlines: delimitter used to split each line of text
        splitline: delimitter used to split the values of each line (typically just " ")
        start: *Optional* Indicates when to start parsing text string. Used to ignore header
                information. By default, program doesn't begins parsing/serialzing immediately
    Returns
    --------
        List of dictionaries
    '''
    data = []
    parse = start == ""
    # for each line, create dictionary object and append
    # to data list.
    for line in txt.split(splitlines):
        # "and line" because we want to ignore empty text lines too
        if parse and line:
            values = line.split(splitline)
            try:
                # Converts keys and values into a dictionary
                # then appends to data list
                data.append({keys[i]:values[i] for i in range(len(keys))}) 
            except IndexError as e:
                # Error handling
                print("Lengths of values and keys DO NOT MATCH!")
                raise(e)
        if line.strip() == start.strip():
            parse = True
    return data

def make_output_table_row(strings:List[str])->str:
    '''
    Description
    -------
        Helper function. Converts a list of strings into a HTML table row
    Args
    -------
        strings - List of strings
    Returns
    --------
        String that contains a HTML row "element" of a "table" element tag
    '''
    return "".join([f"{text} - " for text in strings])

def convert_data(data_to_convert:List[dict], convert_map:dict) -> List[dict]:
    '''
    Description
    -----------
        Performs unit conversion for the value pairs of objects (in a list). 
    Parameters
    -----------
        - data_to_convert: list of objects (dicts) to be converted
        - convert_map: special dictionary to convert multiple different key-value pairs for a given object; 
            - Each key of the convert_map is the conversion 
                factor (float) normalized for the original unit. E.g. 1 mile = 1.6 km,
                so the key would be 1.6 if wanting to convert from miles to km.

            - The value of each key should contain a list of the target keys to the OBJECT
                for which the associated conversion factor should be applied. E.g.
                ["x_distance", "y_distance", "z_distance"] would be the keys found in
                each object of data_to_convert, and be converted using the conversion factor (a key of the convert_map). 
    Returns
    -----------
        Converted data (list of objects)
    '''
    # iterate each object (dictionary) in the list
    for item in data_to_convert:
        # for each object, iterate through each set of conversions
        for conversion_factor, object_keys in convert_map.items():
            # for each set of conversion, apply the conversion factor to "all" its key-value pairs
            for object_key in object_keys:
                # error handling 
                try:
                    item[object_key] = float(item[object_key])*float(conversion_factor)
                except ValueError:
                    raise ValueError(f"ERROR converting {item[object_key]} and {conversion_factor} to float!")
                except KeyError:
                    raise KeyError(f"ERROR: {item} does not have key {object_key} !")
    return data_to_convert
def get_closest_epoch(current_time:float = 0) -> tuple:
    '''
    Description
    -----------
        - Searches for a given epoch closest to the current time
            using binary search (assuming the epochs are always sorted in ascending order)
    Parameters
    -----------
        - current_time: time (seconds) since the epoch in UTC
    Returns
    -----------
        - ISS state vector (object) closest to the current time,
            and the delay between the ISS epoch and the current 
            in seconds.
    '''

    global data
    iss_data = data["data"]

    # If data is empty we must return an empty string
    if len(iss_data) == 0: return ""

    # if current time == 0 we know to default current_time to the real time.
    # Otherwise, we keep the time inputed by the "user"
    current_time = time.time() if current_time == 0 else current_time
    
    # Binary Search
    left, right = 0, len(iss_data) - 1
    mid = (left + right) // 2
    while 0 <= left and right < len(iss_data):
        # intializing epoch, and converting to seconds
        epoch = iss_data[mid]["epoch"]
        epoch_seconds = time.mktime(time.strptime(epoch[:-4], '%Y-%m-%dT%H:%M:%S'))
        
        if math.isclose(epoch_seconds, current_time):
            # returns state vectors w/ exact epochs
            return (iss_data[mid], (epoch_seconds - current_time))
        elif not left < right:
            # returns state vectors w/ closest epoch
            return (iss_data[mid], (epoch_seconds - current_time))
        elif epoch_seconds < current_time:
            left = mid + 1
        elif epoch_seconds > current_time:
            right = mid - 1
        else:
            # Error handling
            print("you've missed some other edge case!")
       
        # updating variables
        mid = (left + right) // 2

def get_error_payload(msg, err_code):
    return {"ERROR": err_code, "message": msg}
def get_success_payload(msg):
    return {"success": True, "message": msg}
## END OF HELPER FUNCTIONS

## ROUTES

@app.route("/", methods=["GET"])
def get_data() -> List[dict]:
    '''
    Description
    -------
        Retrieves data from global "data" varibles. Takes 
        optional query parameter "limit" (int) to limit the length of the list returned
    Args
    -------
        None    
    Returns
    --------
    (Modiified) list of dictionaries containing ISS state vectors
    '''
    global data # initializing global variable "data"
    
    iss_data = data["data"] # retrives the list of ISS state vectors

    # Try block searches for optional query parameters
    # "limit" and "offset". Handles negative or non-integer input edge cases 
    try:
        limit = int(request.args.get('limit', 2**31 - 1))
        if limit < 0: raise(ValueError) # catches negatives parameter inputs

        offset = int(request.args.get('offset', 0))
        if offset < 0: raise(ValueError) # catches negatives parameter inputs
    except ValueError:
        return ("ERROR: limit and offset must be a positive intgers", 404)
    
    return iss_data[offset:offset+limit]

@app.route("/epochs", methods=["GET"])
def get_epochs() -> List[str]:
    '''
    Description
    -------
        Collects all epochs from each ISS state vector. Includes
        optional query parameter "limit" (int) to limit the length 
        of the list returned
    Args
    -------
        None    
    Returns
    --------
    List of strings containing ISS epochs (timestamps)
    '''
    global data
    iss_data = data["data"]
    # Try block searches for optional query parameters
    # "limit" and "offset". Handles negative or non-integer input edge cases 
    try:
        limit = int(request.args.get('limit', 2**31 - 1))
        if limit < 0: raise(ValueError) # catches negatives parameter inputs

        offset = int(request.args.get('offset', 0))
        if offset < 0: raise(ValueError) # catches negatives parameter inputs
    except ValueError:
        payload = get_error_payload("ERROR: limit and offset must be a positive intgers", 404)
        return (payload, 404)
    
    return [ISS["epoch"] for ISS in iss_data][offset:offset+limit]

@app.route("/epochs/<epoch>", methods=["GET"])
def get_state_vectors(epoch) -> List[dict]:
    '''
    Description
    -------
        Retrieves the ISS state vector at a given epoch using get_closest_epoch
    Args
    -------
        - <epoch>: **URL Parameter** The epoch (timestamp) at
          which the ISS as a given state vector
    Returns
    --------
        State vector for ISS at that timed epoch (inside a list object)
    '''
    global data
    iss_data = data["data"]

    # First we check that the data exists
    if len(iss_data) == 0:
        payload = get_error_payload("no data can be found", 404)
        return (payload, 404)

    try:
        # convert desired epoch to seconds
        epoch_seconds = time.mktime(time.strptime(epoch[:-4], '%Y-%m-%dT%H:%M:%S'))
        
        # calling get_cloesest_epoch() since binary search is performed
        ISS, _ = get_closest_epoch(epoch_seconds)

        # if the returned epoch is the same as the desired epoch, we return
        # the ISS state vectors, otherwise we return an empty list
        closest_epoch_seconds = time.mktime(time.strptime(ISS["epoch"][:-4], '%Y-%m-%dT%H:%M:%S'))
        return [ISS] if math.isclose(closest_epoch_seconds, epoch_seconds) else []
    
    except ValueError:
        # if the epoch is not valid, a ValueError exception may be raised
        # when trying to convert it into seconds
        return []

@app.route("/epochs/<epoch>/speed", methods=["GET"])
def get_speed(epoch:str) -> dict:
    '''
    Description
    -------
        Calculates the speed of the ISS at a given epoch (timestamp)
    Args
    -------
        - <epoch>: **URL Parameter** The epoch (timestamp) at
          which the ISS as a given state vector
    Returns
    --------
         The speed (km/s) of the ISS at a given epoch with units (dictionary)
    '''
    global data
    ISS = get_state_vectors(epoch)
    
    # check to make sure epoch is in data before proceeding
    if len(ISS) == 0:
        payload = get_error_payload("Request made for an epoch that does not exists", 404)
        return (payload, 404)
    
    velocity_vectors = [ISS[0]["X_Dot"], ISS[0]["Y_Dot"], ISS[0]["Z_Dot"]]
    try:
        # takes the sum of each velocity vector squared. Then returns root of that sum.
        sum_speeds_squared = sum([float(vector)**2 for vector in velocity_vectors])
        speed = math.sqrt(sum_speeds_squared)
        speed_units_map = {"SI": "km/s", "USCS": "mi/s"} # need to map speed units to correct unit convention (SI/USCS)
        return {"value": speed, "units": speed_units_map[data["units"]]}
    except ValueError:
        payload = get_error_payload("An error occured converting speed to float", 404)
        return (payload, 404)



@app.route("/epochs/<epoch>/location", methods=["GET"])
def get_location(epoch:str) -> dict:
    '''
    Description
    -----------
        - Determines the longitude, latitude, altitude, 
            and geolocation of the ISS at a given epoch
    Parameters
    -----------
        - epoch: epoch of a given ISS state vector 
    Returns
    -----------
        - Location dictionary including keys with information about the l
            longitude, latitude, altitude, and geolocation of the ISS at a given epoch

    '''
    global data
    # retrieve state vector of ISS (a list with one element)
    ISS = get_state_vectors(epoch) 
    if len(ISS) == 0: 
        payload = get_error_payload("no data can be found", 404)
        return (payload, 404)
    
    ISS = ISS[0]
    # retrieve unit appropriate value of mean_earth_radius
    mean_earth_radius = MEAN_EARTH_RADIUS_MAP[data["units"]]

    # extracting hrs and mins
    utc_time = str(datetime.strptime(epoch[:-4], '%Y-%m-%dT%H:%M:%S'))
    hrs = int(utc_time[12:13])
    mins = int(utc_time[15:16])
    
    # calculating longitude, latitude and altitude
    lattitude = math.degrees(math.atan2(ISS["Z"], math.sqrt(ISS["X"]**2 + ISS["Y"]**2)))                
    longitude = math.degrees(math.atan2(ISS["Y"], ISS["X"])) - ((hrs-12)+(mins/60))*(360/24) + 32
    altitude_value = math.sqrt(ISS["X"]**2 + ISS["Y"]**2 + ISS["Z"]**2) - mean_earth_radius
    
    # correcting longitude if it over 180 degrees range
    longitude = -180 + longitude-180 if longitude > 180 else longitude

    # need to map altitude units to correct unit convention (SI/USCS)
    altitude_units_map = {"SI": "km", "USCS": "mi" }
    altitude = {"value": altitude_value, "units": altitude_units_map[data["units"]]}
    
    # Catching cases where geopy is unavailable
    try:
        # determining geolocation
        geocoder = Nominatim(user_agent='iss_tracker')
        geolocation = geocoder.reverse((lattitude, longitude), zoom=1, language='en')
    except requests.exceptions.ReadTimeout:
        logging.warning("Geopy is unavailble right now. Defaulting geolocation to some value")
        geolocation = "Geopy is currently unavailable"
    finally:

        # geolocation will be None if ISS is above an ocean/sea
        if geolocation != None:
            geolocation = geolocation.raw["address"]
        else:
            geolocation = "The ISS is currently above an ocean; Unable to identify geolocation."

        return {"latitude": lattitude, 
                "longitude": longitude, 
                "altitude": altitude, 
                "geolocation": geolocation}


@app.route("/now", methods=["GET"])
def get_now():
    '''
    Description
    -----------
        Determines the current status of the ISS based 
        on the closest epoch to the current time. Status
        information includes speed, location and geolocation.
    Parameters
    -----------
        - None
    Returns
    -----------
        - Dictionary object with four keys of information
            - 'closest_epoch': The clossest epoch to current time, and 
            - 'delay': Distance (in seconds) between closest epoch and current time
            - 'location': Location object including longitude,latitude,altitude, and geolocation
            - 'speed': Current speed of the ISS
    '''
    global data
    iss_data = data["data"]

    # checking if data is empty
    if len(iss_data) == 0: 
        payload = get_error_payload("no data can be found", 404)
        return (payload, 404)
    
    # find closest epoch and its location
    ISS, seconds_delay = get_closest_epoch()
    location = get_location(ISS["epoch"])
    
    # initializing speed and delay
    speed = get_speed(ISS["epoch"])
    delay = {"value": seconds_delay, "units": "seconds"}
    
    # forming payload
    ISS_now = {"closest_epoch": ISS["epoch"], 
               "delay": delay, 
               "location":location,
               "speed": speed
               }
    return ISS_now

@app.route("/convert", methods=["PUT"])
def convert_iss_data() -> str:
    '''
    Description
    -----------
        Converts all ISS data to SI/USCS units using 
        the convert_data() function
    Parameters
    -----------
        "units" : 'USCS' or 'SI' (query parameter)
    Returns
    -----------
        Output text if conversion was successful or unsuccessful
    '''
    global data
    # intializing iss_data and desired units
    iss_data = data["data"]
    desired_units = request.args.get("units", "")
    
    # if current units == desired untis
    if desired_units == data["units"]: 
        return get_success_payload(f"Data is already in {desired_units} units!")
    
    # Converting to SI units
    elif desired_units == "SI":
        convert_map = {1/KM_TO_M: ["X", "Y", "Z", "X_Dot", "Y_Dot", "Z_Dot"]}
        data["data"] = convert_data(iss_data, convert_map)
        data["units"] = desired_units
        return get_success_payload(f"Data has been converted to {desired_units} units")
    
    # Converting to USCS units
    elif desired_units == "USCS":
        convert_map = {KM_TO_M: ["X", "Y", "Z", "X_Dot", "Y_Dot", "Z_Dot"]}
        data["data"] = convert_data(iss_data, convert_map)
        data["units"] = desired_units
        return get_success_payload(f"Data has been converted to {desired_units} units")
    
    # If no units have been inputted
    elif desired_units == "":
        payload = get_error_payload("Invalid query parameter. '/convert' must be used with query parameter 'units' ", 404)
        return (payload, 404)
    
    # If invalid units have been inputted
    else:
        payload = get_error_payload("Only 'SI' and 'USCS' units are supported!", 404)
        return (payload, 404)
    
@app.route("/delete-data", methods=["DELETE"])
def delete_data() -> str:
    '''
    Description
    -------
        Deletes everything from the in-memory dictionary of ISS data
    Args
    -------
        None
    Returns
    --------
        None
    '''
    global data
    # clearing iss list data and units 
    try:
        data["units"] = ""
        data["data"].clear()
        return get_success_payload("data deleted")
    except:
        print("Error occured while trying to delete data")
        payload = get_error_payload("Unable to delete data. Please try again later", 404)
        return (payload, 404)
        

@app.route("/post-data", methods=["POST"])
def post_data() -> str:
    '''
    Description
    -------
        Restores the data to the ISS dictionary by performing a new 
        GET request using the Python requests library.
    Args
    -------
        None
    
    Returns
    --------
        Dictionary with succes information
    '''
    global data 
    try:
        data = {"data": load_data(), "units": "SI"}
        return get_success_payload("data restored")
    except:
        print("Error occured while trying to post data!")
        payload = get_error_payload("Unable to reload data. Please try again later", 404)
        return payload
@app.route("/comment", methods=["GET"])
def get_comments() -> List[str]:
    '''
    Description
    -----------
        - Function to retrieve the current comments from the ISS dataset
    Parameters
    -----------
        - None
    Returns
    -----------
        - List of strings where each string is a comment line
    '''
    try:
        # retrieve text data from ISS website
        txt = requests.get(DATA_URL).text
        # returns parsed comments data
        return get_data_info(txt, "COMMENT ", "COMMENT End sequence of events", "META_STOP", "list")
    except:
        print("trouble getting comments successfully")
        payload = get_error_payload("Unable to get comments. Please try again later", 500)
        return (payload, 500)
    
@app.route("/header", methods=["GET"])
def get_header() -> dict:
    '''
    Description
    -----------
        - Function to get the current header information from the ISS dataset
    Parameters
    -----------
        - None

    Returns
    -----------
        - Dictionary object containing header information
    '''
    try:
        # retrieve text data from ISS website
        txt = requests.get(DATA_URL).text
        # return header data as dictionary object
        return get_data_info(txt, " = ", "META_START")
    except:
        print("trouble getting header data successfully")
        payload = get_error_payload("Unable to get header. Please try again later", 500)
        return (payload, 500)
    
@app.route("/metadata", methods=["GET"])
def get_metadata() -> dict:
    '''
    Description
    -----------
        - Function to get current metadata of the ISS dataset
    Parameters
    -----------
        - None
    Returns
    -----------
        - Dictionary object containing metadata information
    '''
    try:
        # retrieve text data from ISS website
        txt = requests.get(DATA_URL).text
        # return metadata in dictionary object
        return get_data_info(txt, " = ", "META_STOP", "META_START")
    except:
        print("trouble getting metadata successfully")
        payload = get_error_payload("Unable to get metadata. Please try again later", 500)
        return (payload, 500)
    
@app.route("/help", methods=['GET'])
def get_help():
    '''
    Description
    -------
        A human readable string to the screen that 
        gives a brief description of all the available 
        routes including their methods.

    Args
    -------
        None
    
    Returns
    --------
         String text similar to the output of a command line tool
    '''
    horizontal_line = "="*100
    # update for new routes at the end of everything
    return f'''ISS TRACKER API


{make_output_table_row(["ROUTES", "METHOD", "DESCRIPTION"])}
{horizontal_line}

{make_output_table_row(['"/"', "GET", "Return entire data set"])}

{make_output_table_row(['"/epochs"', "GET", "Return list of all Epochs in the data set"])}

{make_output_table_row(['"/epochs?limit=int&offset=int"', "GET", "Return modified list of Epochs given query parameters"])}

{make_output_table_row(['"/epochs/<epoch>"', "GET", "Return state vectors for a specific Epoch from the data set"])}

{make_output_table_row(['"/epochs/<epoch>;/speed"', "GET", "Returns instantaneous speed for a specific Epoch in the data set"])}

{make_output_table_row(['"/help"', "GET", "Returns help text (this right here!)"])}

{make_output_table_row(['"/delete-data"', "DELETE", "Deletes all data from the API's memory"])}

{make_output_table_row(['"/post-data"', "POST", "Reloads all the data from the Internalnationa Space Station Data website"])}
'''
## END OF ROUTES

## GLOBAL VARIABELS
data = {"data": load_data(), "units": "SI"}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
