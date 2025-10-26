import argparse
import base64
import os
import requests
import sys

BASE_URL = "http://127.0.0.1:5000"  # API URL

def login(username, password):
    """Login and get Bearer token."""
    resp = requests.post(f"{BASE_URL}/login", json={
        "username": username,
        "password": password
    })

    if resp.status_code != 200:
        print(f"[Error] Login failed: {resp.text}")
        sys.exit(1)

    token = resp.json().get("access_token")
    if not token:
        print("[Error] Don't received access token from server.")
        sys.exit(1)
    return token


def call_api(endpoint, token, method="GET", data=None):
    """API call with Bearer token."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{endpoint}"

    if method.upper() == "GET":
        resp = requests.get(url, headers=headers, json=data)
    else:
        resp = requests.post(url, headers=headers, json=data)

    print(f"[API Call] {method} {url} - Status: {resp.status_code}")

    try:
        print(resp.json())
        return resp.json()
    except Exception:
        print(resp.text)
        return resp.text

def SendMessage(username=None, password=None, deviceId=None, message=None, ask=False):
    if ask:
        username = input("Enter Username: ")
        password = input("Enter Password: ")
        deviceId = input("Enter Device ID: ")
        message = input("Enter Message: ")

    token = login(username, password)
    call_api("/send-message", token, "POST", {
        "deviceId": deviceId,
        "message": message
    })


def SendInfo(username=None, password=None, deviceId=None, batteryLevel=None, coreTemp=None, houseTemp=None, ask = False):

    if ask:
        username = input("Enter Username: ")
        password = input("Enter Password: ")
        deviceId = input("Enter Device ID: ")
        batteryLevel = input("Enter Battery Level: ")
        coreTemp = input("Enter Core Temperature: ")
        houseTemp = input("Enter House Temperature: ")

    token = login(username, password)
    return call_api("/send-info", token, "POST", {
        "deviceId": deviceId,
        "batteryLevel": batteryLevel,
        "coreTemp": coreTemp,
        "houseTemp": houseTemp
    })

def GetDevices(username=None, password=None, ask=False):
    if ask:
        username = input("Enter Username: ")
        password = input("Enter Password: ")

    token = login(username, password)
    return call_api("/get-devices", token)

def GetDeviceInfo(username=None, password=None, deviceId=None, ask=False):
    if ask:
        username = input("Enter Username: ")
        password = input("Enter Password: ")
        deviceId = input("Enter Device ID: ")

    token = login(username, password)
    return call_api(f"/get-device-info?deviceId={deviceId}", token)



def GetCameraConfiguration(username=None, password=None, ask=False):
    if ask:
        username = input("Enter Username: ")
        password = input("Enter Password: ")

    token = login(username, password)
    return call_api("/get-camera-configuration", token)

def ConfigureCamera(username=None, password=None, cameraConfig=None, ask=False):
    if ask:
        username = input("Enter Username: ")
        password = input("Enter Password: ")
        cameraConfig = {}
        cameraConfig["used-camera"] = input("Enter Used Camera: ")
        cameraConfig["resolution"] = input("Enter Resolution: ")
        cameraConfig["auto-focus"] = input("Enter Auto Focus (true/false): ")
        cameraConfig["focal-length"] = input("Enter Focal Length: ")
        cameraConfig["contrast"] = input("Enter Contrast: ")
        cameraConfig["saturation"] = input("Enter Saturation: ")
        cameraConfig["white-balance"] = input("Enter White Balance: ")
        cameraConfig["iso"] = input("Enter ISO: ")
        cameraConfig["shutter-speed"] = input("Enter Shutter Speed: ")

    token = login(username, password)
    return call_api("/configure-camera", token, "POST", cameraConfig)


def SendImage(username=None, password=None, imagePath=None, ask=False):
    """Elküldi a képet base64-ben a /send-image végpontnak"""
    if ask:
        username = input("Enter Username: ")
        password = input("Enter Password: ")
        imagePath = input("Image path: ")

    token = login(username, password)

    if not os.path.exists(imagePath):
        print(f"[Error] File not found: {imagePath}")
        return

    # Beolvassuk és base64 kódoljuk a képet
    with open(imagePath, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")

    payload = {
        "image": encoded
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"{BASE_URL}/send-image"

    resp = requests.post(url, headers=headers, json=payload)

    print(f"[API Call] POST {url} - Status: {resp.status_code}")

    try:
        print(resp.json())
        return resp.json()
    except Exception:
        print(resp.text)
        return resp.text
    
    

def main():
    parser = argparse.ArgumentParser(description="Beacon API client")

    parser.add_argument("command", help="What do you want to do?",
                        choices=["ping", "get-devices", "get-device-info",
                                 "get-messages", "get-images", "send-message", "send-image",
                                 "send-info", "get-camera-configuration", "configure-camera"])

    args = parser.parse_args()

    if args.command == "ping":
        call_api("/ping", None)
    elif args.command == "send-message":
        SendMessage(ask=True)
    elif args.command == "get-device-info":
        GetDeviceInfo(ask=True)
    elif args.command == "get-devices":
        GetDevices(ask=True)
    elif args.command == "send-info":
        SendInfo(ask=True)
    elif args.command == "get-camera-configuration":
        GetCameraConfiguration(ask=True)
    elif args.command == "configure-camera":
        ConfigureCamera(ask=True)
    elif args.command == "send-image":
        SendImage(ask=True)

if __name__ == "__main__":
    main()
