from tinydb import TinyDB, Query
import datetime
import json

def UpdateBeaconData(deviceId, batteryLevel = None, controllerBattery = None, coreTemp = None, houseTemp = None, latency = None):
    """
    Update the beacon information in the database.

    :param deviceId: The ID of the beacon to update.
    :param batteryLevel: The updated battery level of the beacon.
    :param coreTemp: The updated core temperature of the beacon.
    :param houseTemp: The updated house temperature of the beacon.
    """
    db = TinyDB("database/beacons.json")
    query = Query()
    
    # Check if the device exists in the database
    if not db.contains(query.deviceId == deviceId):
        # If not, create a new entry
        db.insert({"deviceId": deviceId, "batteryLevel": batteryLevel, "controllerBattery": controllerBattery, "coreTemp": coreTemp, "houseTemp": houseTemp, "latency": latency, "lastActivity": datetime.datetime.now().isoformat()})
        print(f"Device {deviceId} not found in the database. Created a new entry.")
    else:
        # Update the existing device information
        data = {}
        if batteryLevel is not None:
            data["batteryLevel"] = batteryLevel
        if controllerBattery is not None:
            data["controllerBattery"] = controllerBattery
        if coreTemp is not None:
            data["coreTemp"] = coreTemp
        if houseTemp is not None:
            data["houseTemp"] = houseTemp
        if latency is not None:
            data["latency"] = latency

        data["lastActivity"] = datetime.datetime.now().isoformat()
        
        db.update(data, query.deviceId == deviceId)
        print(f"Device {deviceId} updated successfully.")


def UpdateCameraConfiguration(cameraConfig):
    """
    Update the camera configuration for a specific device.

    :param cameraConfig: The new camera configuration data.
    """
    
    with open("database/camera-config.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if "Brightness" in cameraConfig:
        data["Brightness"] = float(cameraConfig["Brightness"])
    if "Saturation" in cameraConfig:
        data["Saturation"] = float(cameraConfig["Saturation"])
    if "Sharpness" in cameraConfig:
        data["Sharpness"] = float(cameraConfig["Sharpness"])
    if "ExposureValue" in cameraConfig:
        data["ExposureValue"] = float(cameraConfig["ExposureValue"])
    if "ExposureTime" in cameraConfig:
        data["ExposureTime"] = int(cameraConfig["ExposureTime"])
    if "LensPosition" in cameraConfig:
        data["LensPosition"] = float(cameraConfig["LensPosition"])
    if "Autofocus" in cameraConfig:
        data["AfMode"] = int(cameraConfig["Autofocus"])
    if "AutoExposure" in cameraConfig:
        data["AeEnable"] = bool(cameraConfig["AutoExposure"])
    if "HdrMode" in cameraConfig:
        data["HdrMode"] = int(cameraConfig["HdrMode"])

    with open("database/camera-config.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
