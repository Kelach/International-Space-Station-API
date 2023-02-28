from flask import Flask, request
from typing import List
import math
import requests
app = Flask(__name__)
DATA_URL = "https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.txt"

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
    # Initalize the keys of our data dictionaries
    keys = ["epoch", "X", "Y", "Z", "X_Dot", "Y_Dot", "Z_Dot"]
    
    # retrieve text data from ISS website
    unparsed_data = requests.get(DATA_URL).text
    
    # return list of dictionaries using txt_to_dict()
    data = txt_to_dict(unparsed_data, keys, "\r\n", " ", "COMMENT End sequence of events")
    return data


def txt_to_dict(txt: str, keys: List[str], splitlines: str, splitline: str, start: str = "") -> List[dict]:
    '''
    Description
    -------
        Serializes a given text into list of dictionaries where each dictionary
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
                # serializes keys and values into a dictionary
                # then appends to data list
                data.append({keys[i]:values[i] for i in range(len(keys))}) 
            except IndexError as e:
                print("Lengths of values and keys DO NOT MATCH!")
                raise(e)
        if line.strip() == start.strip():
            parse = True
    return data

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
    
    # Try block searches for optional query parameters
    # "limit" and "offset". Handles negative or non-integer input edge cases 
    try:
        limit = int(request.args.get('limit', 2**31 - 1))
        if limit < 0: raise(ValueError) # catches negatives parameter inputs

        offset = int(request.args.get('offset', 0))
        if offset < 0: raise(ValueError) # catches negatives parameter inputs
    except ValueError:
        return ("ERROR: limit and offset must be a positive intgers", 404)
    
    return data[offset:offset+limit]

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
    data = get_data()
    
    # Try block searches for optional query parameters
    # "limit" and "offset". Handles negative or non-integer input edge cases 
    try:
        limit = int(request.args.get('limit', 2**31 - 1))
        if limit < 0: raise(ValueError) # catches negatives parameter inputs

        offset = int(request.args.get('offset', 0))
        if offset < 0: raise(ValueError) # catches negatives parameter inputs
    except ValueError:
        return ("ERROR: limit and offset must be a positive intgers", 404)
    
    return [ISS["epoch"] for ISS in data][offset:offset+limit]

@app.route("/epochs/<epoch>", methods=["GET"])
def get_state_vectors(epoch) -> List[dict]:
    '''
    Description
    -------
        Retrieves the ISS state vector at a given epoch
    Args
    -------
        - <epoch>: **URL Parameter** The epoch (timestamp) at
          which the ISS as a given state vector
    Returns
    --------
        State vector for ISS at that timed epoch
    '''
    data = get_data()
    # iterate through list and only keep objects with desired epoch value
    return [ISS for ISS in data if ISS.get("epoch") == epoch]

@app.route("/epochs/<epoch>/speed", methods=["GET"])
def get_speed(epoch) -> str:
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
         The speed (km/s) of the ISS at a given epoch (formatted into a string)
    '''
    state_vectors = get_state_vectors(epoch)
    # check to make sure epoch is in data before proceeding
    if len(state_vectors) == 0:
        return ("ERROR: Request made for an epoch that does not exists\n", 404)
    
    velocity_vectors = [state_vectors[0]["X_Dot"], state_vectors[0]["Y_Dot"], state_vectors[0]["Z_Dot"]]
    try:
        # takes the sum of each velocity vector squared. Then returns root of that sum.
        speed_squared = sum([float(vector)*float(vector) for vector in velocity_vectors])
        speed = math.sqrt(speed_squared)
        return f"speed: {speed:.3f} km/s\n"
    except ValueError:
        return ("Error converting speed to float")

@app.route("/delete-data", methods=["DELETE"])
def delete_data():
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
    data.clear()
    return "Data deleted!\n"

@app.route("/post-data", methods=["POST"])
def post_data():
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
        None
    '''
    global data 
    data = load_data()
    return "Data Restored!\n"

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
# global varible "data". Flask application always starts with
# all data.
data = load_data()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
