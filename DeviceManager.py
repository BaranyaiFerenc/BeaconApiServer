from tinydb import TinyDB, Query
import datetime
import json

def UpdateBeaconData(deviceId, batteryLevel = None, controllerBattery = None, coreTemp = None, houseTemp = None):
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
        db.insert({"deviceId": deviceId, "batteryLevel": batteryLevel, "controllerBattery": controllerBattery, "coreTemp": coreTemp, "houseTemp": houseTemp, "lastActivity": datetime.datetime.now().isoformat()})
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

    if "used-camera" in cameraConfig:
        data["used-camera"] = cameraConfig["used-camera"]
    if "resolution" in cameraConfig:
        data["resolution"] = cameraConfig["resolution"]
    if "auto-focus" in cameraConfig:
        data["auto-focus"] = cameraConfig["auto-focus"]
    if "focal-length" in cameraConfig:
        data["focal-length"] = cameraConfig["focal-length"]
    if "contrast" in cameraConfig:
        data["contrast"] = cameraConfig["contrast"]
    if "saturation" in cameraConfig:
        data["saturation"] = cameraConfig["saturation"]
    if "white-balance" in cameraConfig:
        data["white-balance"] = cameraConfig["white-balance"]
    if "iso" in cameraConfig:
        data["iso"] = cameraConfig["iso"]
    if "shutter-speed" in cameraConfig:
        data["shutter-speed"] = cameraConfig["shutter-speed"]

    with open("database/camera-config.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
