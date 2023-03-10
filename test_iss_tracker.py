from iss_tracker import get_header, get_metadata, get_comments, convert_data, get_location, get_closest_epoch, get_now
import pytest

def main():
    pass
    # test_get_header()
    # test_get_metadata()
    # test_get_comments()
    # test_convert_data()
    # test_get_location()
    # test_get_closest_epoch()
    # test_get_now()

def test_get_header():
    global txt
    header = get_header()
    assert len(header) == 3
    assert header["ORIGINATOR"] == "NASA/JSC/FOD/TOPO"


def test_get_metadata():
    global txt
    metadata = get_metadata()
    assert len(metadata) == 9
    assert metadata["OBJECT_NAME"] == "ISS"
    assert metadata["OBJECT_ID"] == "1998-067-A"
    assert metadata["CENTER_NAME"] == "Earth"

def test_get_comments():
    global txt
    comments = get_comments()
    assert comments[0] == "Source: This file was produced by the TOPO office within FOD at JSC."
    assert comments[1] == "Units are in kg and m^2"
    assert "MASS=" in comments[2]
    assert "DRAG_AREA=" in comments[3]
    assert "DRAG_COEFF=" in comments[4]
    assert "SOLAR_RAD_AREA=" in comments[5]

def test_convert_data():
    data = [
        {
            "X": "-3386.674055588920",
            "X_Dot": "-5.48416835093778",
        },
        {
            "X": "-4563.767820418440",
            "X_Dot": "-4.26470872233791",
        },
        {
            "X": "-5408.677713120010",
            "X_Dot": "-2.73284888629213",
        }]
    converted_data = convert_data(data, {0.6213711922: ["X", "X_Dot"]})
    assert converted_data[0]["X"] == pytest.approx(-2104.381695640534417)
    assert converted_data[0]["X_Dot"] == pytest.approx(-3.407704226652461976)
    assert converted_data[1]["X"] == pytest.approx(-2835.793851667785475)
    assert converted_data[1]["X_Dot"] == pytest.approx(-2.649967143344064358)
    assert converted_data[2]["X"] == pytest.approx(-3360.796519028877356)
    assert converted_data[2]["X_Dot"] == pytest.approx(-1.698113570679810946)
    
def test_get_location():
    location = get_location("2023-03-04T08:31:00.000")
    assert len(location) == 3
    print(location)

def test_get_closest_epoch():
    epoch1, seconds1 = get_closest_epoch()
    epoch2, seconds2 = get_closest_epoch()
    epoch3, seconds3 = get_closest_epoch()
    assert abs(seconds1 - seconds3) < 1
    assert abs(seconds2 - seconds3) < 1
    assert abs(seconds1 - seconds2) < 1

def test_get_now():
    response = get_now()
    print(response)
    assert len(response) == 5
    assert response["closest_epoch"] == get_closest_epoch()[0]

def test_get_epochs():
    pass

txt = '''CCSDS_OEM_VERS = 2.0
CREATION_DATE  = 2023-02-16T00:51:05.746
ORIGINATOR     = NASA/JSC/FOD/TOPO

META_START
OBJECT_NAME          = ISS
OBJECT_ID            = 1998-067-A
CENTER_NAME          = Earth
REF_FRAME            = EME2000
TIME_SYSTEM          = UTC
START_TIME           = 2023-02-15T12:00:00.000
USEABLE_START_TIME   = 2023-02-15T12:00:00.000
USEABLE_STOP_TIME    = 2023-03-02T12:00:00.000
STOP_TIME            = 2023-03-02T12:00:00.000
META_STOP

COMMENT Source: This file was produced by the TOPO office within FOD at JSC.
COMMENT Units are in kg and m^2
COMMENT MASS=460724.00
COMMENT DRAG_AREA=1504.78
COMMENT DRAG_COEFF=3.25
COMMENT SOLAR_RAD_AREA=0.00
COMMENT SOLAR_RAD_COEFF=0.00
COMMENT Orbits start at the ascending node epoch
COMMENT ISS first asc. node: EPOCH = 2023-02-15T12:15:31.146 $ ORBIT = 2291 $ LAN(DEG) = -117.91539
COMMENT ISS last asc. node : EPOCH = 2023-03-02T11:19:04.946 $ ORBIT = 2523 $ LAN(DEG) = 167.36584
COMMENT Begin sequence of events
COMMENT TRAJECTORY EVENT SUMMARY:
COMMENT 
COMMENT |       EVENT        |       TIG        | ORB |   DV    |   HA    |   HP    |
COMMENT |                    |       GMT        |     |   M/S   |   KM    |   KM    |
COMMENT |                    |                  |     |  (F/S)  |  (NM)   |  (NM)   |
COMMENT =============================================================================
COMMENT  82P Undock            049:02:26:30.000             0.0     424.8     407.0
COMMENT                                                    (0.0)   (229.4)   (219.8)
COMMENT 
COMMENT  GMT 051 ISS Reboost   051:02:58:00.000             1.7     425.4     406.2
COMMENT                                                    (5.6)   (229.7)   (219.3)
COMMENT 
COMMENT  69S Launch            055:00:34:00.000             0.0     426.2     410.3
COMMENT                                                    (0.0)   (230.1)   (221.6)
COMMENT 
COMMENT  69S Docking           057:01:01:00.000             0.0     426.2     409.4
COMMENT                                                    (0.0)   (230.1)   (221.1)
COMMENT 
COMMENT  Crew06 Launch         057:07:07:35.000             0.0     426.3     409.6
COMMENT                                                    (0.0)   (230.2)   (221.2)
COMMENT 
COMMENT  Crew06 Docking        058:06:05:00.000             0.0     426.2     409.1
COMMENT                                                    (0.0)   (230.1)   (220.9)
COMMENT 
COMMENT =============================================================================
COMMENT End sequence of events
'''

if __name__ == "__main__":
    main()

