import time
import BeaconShell
import random

username = "beacon"
password = "Beacon123"
deviceId = "Beacon_1"

batteryLevel = 75
coreTemp = 30
houseTemp = 22

msgIndex = 0

while True:
    BeaconShell.SendInfo(username=username, password=password, deviceId=deviceId, batteryLevel=batteryLevel, coreTemp=coreTemp, houseTemp=houseTemp)
    batteryLevel -= 0.01
    coreTemp += random.uniform(-0.05, 0.05)
    houseTemp += random.uniform(-0.01, 0.01)
    houseTemp -= 0.002
    time.sleep(10)

    if random.random() < 0.5:
        BeaconShell.SendMessage(username=username, password=password, deviceId=deviceId, message=f"Hello from DummyBeacon! Message index: {msgIndex}")
        msgIndex += 1

    time.sleep(2)