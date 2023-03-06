# International Space Station API using Flask

## Project Objective

Easily query and modify information on the whereabouts of the [International Space Station](https://en.wikipedia.org/wiki/International_Space_Station) using the International Space Station Web API! This Flask application supports querying positional, velocity, and locational data about the ISS. ISS API serves as an intermediary between the [ISS Trajectory Data Webiste](https://spotthestation.nasa.gov/trajectory_data.cfm) and the end user. The ISS trajectory data set contains an abundance of measuring data about the ISS, and it can be challenging to sift through the data manually to find what you are looking for. With this application, you can easily query and parse information regarding the trajectory of the ISS.

## Data Set

- ### Access
  The ISS positional and velocity data set can be accessed from the [ISS Trajectory Data Webiste](https://spotthestation.nasa.gov/trajectory_data.cfm). 

- ### Description
  The data set includes a header, metadata, and comments which include additional information about the ISS like its mass (kg) and drag coefficient (m^2). 
  
  After the additional information, ISS state vectors in the **Mean of J2000 (J2K) reference frame** are listed at four-minute intervals spanning a total length of 15 days. 
    
    - In case you're wondering, having ISS state vectors in the Mean of J2000 (J2K) reference frame essentially means the positional and velocity values calculated for the ISS are relative to the Earth's equator and equinox.  
  
  Each state vector includes an epoch (time in Universal Coordinated Time), position vectors X, Y, and Z (km), and velocity vectors X_Dot, Y_Dot, and Z_Dot (km/s).
    - Note: You can switch to USCS units (mi/s) if you wish to instead. (see [routes](#routes) for more info)


## Script
- ### *[iss_tracker.py](./iss_tracker.py)*
  - Flask Application that parses and returns to the end user information about the ISS such as its position as velocity. This flask application relies on the text file format version provided by the [ISS Trajectory Data Webiste](https://spotthestation.nasa.gov/trajectory_data.cfm). 
  - To view the currently supported routes, see the [Running the App](#running-the-app) section
  
## Installation 
To get a copy of the project up and running on your local machine, you have three options:

- [Install/Run via the Docker Hub](#installrun-via-the-docker-hub)

- [Install/Run via the Dockerfile](#installrun-via-the-dockerfile)

- [Install/Run via Git clone](#installrun-via-git-clone)

If you're wondering "what's the difference?" Here's a small description for each installation option:

- **via the Docker Hub**: 
    - Easiest installation method, but you'll need Docker installed on your local machine.([install Docker here](https://docs.docker.com/get-docker/))
- **via the Dockerfile**: 
    - Helpful if you'd rather build the Docker image locally instead of pulling it from the Docker Hub. (not reccommended if you'd like to maintain the latests image for this application). You'll also still need Docker installed.
    - Also, building the Docker image for this application yourself gives you the freedom to modify the source code of the [iss_tracker.py](./iss_tracker.py) script and even the Docker image itself!
- **via Git Clone**:
    - This method is also helpful if you'd like to modify the source code, but without using Docker to run the application. However, system differences between my computer and yours may prevent this application from running as intended on your local computer.
    
**NOTE**: You'll need a reliable network connection and Python3 installed to proceed with any of the three installation methods! (see this application was built using Python 3.8).


## Install/Run via the Docker Hub
First, ensure you have Docker installed on your local machine. To run the app you will need to follow these steps:

  1. Pull the Docker image from the public registry by running the following command:
      
          docker pull kelach/iss_api:1.0
  
  2. Now, you can run a container of the image with the following command:
      
          docker run -it --rm -p 5000:5000 kelach/iss_api:1.0
          
        - Incase you're new to running Docker images:
            - `-it` : Allows you to interact in your container using your terminal
            - `--rm` : removes the container after exiting the Flask application
            - `-p` : Binds port 5000 on the container to the port 5000 on your local/remote computer (so you can communicate with the flask program!)
      
  3. Now that the Flask application is running you can navigate to http://localhost:5000/ in your web browser to access the data and you're all set! See [Routes](#routes) for the supported routes.

## Install/Run via the Dockerfile
  First, ensure you have Docker installed on your local machine. To build the Docker image on your local computer, see the following steps:
  
 1. Clone this repository to your local machine by the following in your command terminal:
      
          git clone https://github.com/Kelach/coe-332-sp23.git
  
 2. In your command terminal cd into this repository by running: 
      
          cd /path/to/International-Space-Station-API
          
    - Where you replace "/path/to/International-Space-Station-API/" with the path to this directory.
      
 3. Next, build the Docker image you just pulled by running this command:
    
        docker build -t kelach/iss_api:1.0 .

4. Now, you can run a container of the image with the following command:
    
        docker run -it --rm -p 5000:5000 kelach/iss_api:1.0
        
      - Incase you're new to running Docker images:
          - `-it` : Allows you to interact in your container using your terminal
          - `--rm` : removes the container after exiting the Flask application
          - `-p` : Binds port 5000 on the container to the port 5000 on your local/remote computer (so you can communicate with the flask program!)
  
  4. Now that the Flask application is running you can navigate to http://localhost:5000/ in your web browser to access the data and you're all set! See [Routes](#routes) for the supported routes.
   
## Install/Run via Git Clone 
Ensure that you have python 3.8.10+ installed on your local computer. To run the app, you will need to follow these steps:

1. Clone this repository to your local machine by running:

        git clone https://github.com/Kelach/coe-332-sp23.git

 2. In your command terminal cd into this repository by running: 
      
          cd /path/to/International-Space-Station-API
          
    - Where you replace "/path/to/International-Space-Station-API/" with the path to this directory.

3. To install to install the dependencies for this project, run this command in your terminal:
        
        pip3 install -r requirements.txt

3. Start the Flask server by running: 

        flask --app iss_tracker   

    - If you'd like to run this application in debug mode you can run this command to start the flask app instead:
        
        ``` 
        flask --app iss_tracker --debug run 
        ```

4. Lastly, Navigate to http://localhost:5000/ in your web browser to access the application and you're all set! See [Routes](#routes) for the supported routes.

## Routes
  Here are the currently supported routes and query parameters:
  | Route | Method | Returned Data
  |-------|---------|---------|
  | `/` | `GET` |The entire data set (list of dictionaries)  <br><em> - Includes optional parameters "limit" (positive int) to truncate results and "offset" (positive int) to change the starting position at which the data is returned </em></br> See [examples](#example-queries-and-results) below |
  | `/comment` | `GET` | Returns comments from the ISS trajectory data source file |
  | `/header` | `GET` | Returns header information from the ISS trajectory data source file |
  | `/metadata` | `GET` | Returns metadata from the ISS trajectory data source file |
  | `/now` | `GET` | Returns latitude, longitude, altidue, and geoposition of the ISS for an epoch that is nearest in time |
  | `/epochs` | `GET` | All Epochs in the data set (list of strings) <br><em> - Includes optional parameters "limit" (positive int) to truncate results and "offset" (positive int) to change the starting position at which the data is returned</em></br> See [examples](#example-queries-and-results) below |
  | `/epochs/<epoch>` | `GET` | State vectors for a specific Epoch from the data set (list of one dictionary) <br> <b> &lt;epoch&gt; </b> Takes string inputs only.</br> See [examples](#example-queries-and-results) below |
  | `/epochs/<epoch>/location` | `GET` | Returns latitude, longitude, altitude, and geoposition of the ISS for a given epoch |
  | `/help` | `GET` | Help text (string; not html friendly) that briefly describes each route |
  | `/convert?units` | `PUT` | Converts data from 'SI' to 'USCS' and vice versa. The data is originally in SI units. See [example queries](#example-queries-and-results) for more|
  | `/delete-data` | `DELETE` | Deletes all stored data in the application |
  | `/post-data` | `POST` | Reloads flask application with the original ISS trajectory data |
  
  
  
## Example Queries and Results
  - Note: you may need to add quotes ("") surrounding your queries if you are using a terminal 
    - e.g. `"http://localhost:5000/epochs/2023-02-15T12:16:00.000"`
    instead of: `http://localhost:5000/epochs/2023-02-15T12:16:00.000`

<table>
<tr>
<td> 

### Route 

</td>
<td> 

### Returned Data

</td>
</tr>
<tr>
<td> 

`http://localhost:5000?limit=3` 

</td>
<td>
    
```json
[
  {
    "X": "-4788.368507507620",
    "X_Dot": "-4.47317640532645",
    "Y": "1403.549622371260",
    "Y_Dot": "-5.44388258946684",
    "Z": "-4613.109479300690",
    "Z_Dot": "2.99705738521092",
    "epoch": "2023-02-15T12:00:00.000"
  },
  {
    "X": "-5675.021705065900",
    "X_Dot": "-2.87004030254429",
    "Y": "61.910987386751",
    "Y_Dot": "-5.66832649751615",
    "Z": "-3734.576449237840",
    "Z_Dot": "4.27967238757376",
    "epoch": "2023-02-15T12:04:00.000"
  },
  {
    "X": "-6148.993248504040",
    "X_Dot": "-1.05503300582525",
    "Y": "-1284.195507156520",
    "Y_Dot": "-5.48063337615216",
    "Z": "-2583.725124493340",
    "Z_Dot": "5.25228914094105",
    "epoch": "2023-02-15T12:08:00.000"
  }
]
```
</td>
</tr>

<tr>
<td>

`http://localhost:5000/comment` 

</td>
<td>
    
```json
[
  "Source: This file was produced by the TOPO office within FOD at JSC.",
  "Units are in kg and m^2",
  "MASS=473413.00",
  "DRAG_ARE...",
]
```

</td>
</tr>

<tr>
<td>

`http://localhost:5000/header` 

</td>
<td>
    
```json
{
  "CCSDS_OEM_VERS": "2.0",
  "CREATION_DATE": "2023-03-04T04:34:04.606",
  "ORIGINATOR": "NASA/JSC/FOD/TOPO"
}

```

</td>
</tr>

<tr>
<td>

`http://localhost:5000/metadata` 

</td>
<td>
    
```json
{
  "CENTER_NAME": "Earth",
  "OBJECT_ID": "1998-067-A",
  "OBJECT_NAME": "ISS",
  "REF_FRAME": "EME2000",
  "STA...": "...",
  "STOP_TIME": "2023-03-18T15:47:35.995",
  "TIME_SYSTEM": "UTC",
  "USEABLE_START_TIME": "2023-03-03T15:47:35.995",
  "USEABLE_STOP_TIME": "2023-03-18T15:47:35.995"
}
```

</td>
</tr>

<tr>
<td>

`http://localhost:5000/now` 

</td>
<td>
    
```json
{
  "closest_epoch": "2023-03-05T21:31:35.995",
  "delay": {
    "units": "seconds",
    "value": -219.1373794078827
  },
  "location": {
    "altitude": {
      "units": "km",
      "value": 417.53296811711516
    },
    "geolocation": "The ISS is currently above an ocean; Unable to identify geolocation.",
    "latitude": 27.488124374989283,
    "longitude": 332.82252940196554
  },
  "speed": {
    "units": "km/s",
    "value": 7.6681216522619655
  }
}
```

</td>
</tr>
<tr>
<td>

`http://localhost:5000/epochs?limit=5` 

</td>
<td>
    
```json
[
  "2023-02-15T12:00:00.000",
  "2023-02-15T12:04:00.000",
  "2023-02-15T12:08:00.000",
  "2023-02-15T12:12:00.000",
  "2023-02-15T12:16:00.000"
]
```

</td>
</tr>

<tr>
<td> 

`http://localhost:5000/epochs/2023-02-15T12:16:00.000`

</td>
<td>

```json
[
  {
    "X": "-5750.560812798620",
    "X_Dot": "2.67584228156696",
    "Y": "-3604.169888126130",
    "Y_Dot": "-3.94766617813937",
    "Z": "186.445271666768",
    "Z_Dot": "6.00579498886775",
    "epoch": "2023-02-15T12:16:00.000"
  }
]

```

</td>
</tr>
<tr>
<td>

`http://localhost:5000/epochs/2023-02-15T12:16:00.000/speed`

</td>
<td>

```json 
{
  "units": "km/s",
  "value": 7.663940629644085
}
```

</td>
</tr>

<tr>
<td>

`http://localhost:5000/epochs/2023-02-15T12:16:00.000/location` 

</td>
<td>
    
```json
{
  "altitude": {
    "units": "km",
    "value": 427.99075304730286
  },
  "geolocation": {
    "ISO3166-2-lvl4": "ID-JA",
    "country": "Indonesia",
    "country_code": "id",
    "county": "Merangin",
    "state": "Jambi"
  },
  "latitude": -1.7412612735011228,
  "longitude": 102.32887684466722
}
```

</td>
</tr>
<tr>
<td>

`http://localhost:5000/help`

</td>
<td>

string text similar to the [Routes](#routes) table

</td>
</tr>
<tr>
<td>

`http://localhost:5000/convert?units=USCS`

</td>
<td>

` 'Data has been converted to USCS units!' `

</td>
</tr>

<tr>
<td>

`http://localhost:5000/delete-data`

</td>
<td>

` 'Data deleted!' `

</td>
</tr>
<tr>
<td>

`http://localhost:5000/post-data`

</td>
<td>

` 'Data Restored!' `

</td>
</tr>
</table>
