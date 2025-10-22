import base64
import datetime
import logging
from functools import wraps
import os
from flask import Flask, render_template, request, jsonify, send_file
import jwt
from werkzeug.security import check_password_hash, generate_password_hash
import json
from tinydb import TinyDB, Query
from flask_sock import Sock

import DeviceManager

app = Flask(__name__)

#######################################
#
#   Audio transmission via WebSocket
#
#######################################


'''


sock = Sock(app)

@app.route('/')
def home():
    return render_template('index.html')


clients = {}

@sock.route("/ws")
def ws_endpoint(ws):
    peer_id = ws.receive()
    if not peer_id:
        return
    clients[peer_id] = ws
    print(f"[SIGNAL] {peer_id} connected")

    try:
        while True:
            msg = ws.receive()
            if msg is None:
                break
            data = json.loads(msg)
            target = data.get("target")
            print(f"[SIGNAL] {peer_id} -> {target}: {data.get('type')}")
            if target and target in clients:
                clients[target].send(json.dumps(data))
    finally:
        if clients.get(peer_id) is ws:
            del clients[peer_id]
        print(f"[SIGNAL] {peer_id} disconnected")
'''
#######################################
#
#   Secured API Endpoints
#
#######################################


# --- decorator that checks the Bearer token in the Authorization header ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return jsonify({"message": "Authorization header missing"}), 401

        # várt formátum: "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"message": "Invalid Authorization header format. Expected: Bearer <token>"}), 401

        token = parts[1]
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # payload tartalmazhat pl. 'sub' (subject) vagy 'user' mezőt
            request.user = payload.get("sub")
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated

# --- bejelentkezés: token kiadása username+password ellenőrzés után ---
@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    # Read the user from the database
    db = TinyDB("database/users.json")
    userQuerry = Query()
    user = db.search(userQuerry.username == username)[0]

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid credentials"}), 401

    # token payload
    payload = {
        "sub": username,  # subject
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # lejárat: 2 óra
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
    # PyJWT v2+ visszaad stringet
    return jsonify({"access_token": token})


#######################################
#
#   Analitic API Endpoints
#
#######################################


# Check the connection with the server
@app.route("/ping")
@token_required
def ping():
    print(f"Ping request from user: {request.user}")
    return jsonify(success=True, message=f"Hello {request.user}, ping successful."), 200


#######################################
#
#   Client API Endpoints
#
#######################################


# Get the existing Beacon devices
@app.route("/get-devices", methods=["GET"])
@token_required
def get_devices():
    db = TinyDB("database/beacons.json")
    devices = [row["deviceId"] for row in db.all() if "deviceId" in row]
    print(f"Get devices request from user: {request.user}")
    return jsonify(success=True, data=devices), 200


# Get the Beacon information based on the device ID
@app.route("/get-device-info", methods=["GET"])
@token_required
def get_device_info():
    device_id = request.args.get('deviceId')

    print(f"Get device info request by: {request.user} for device ID: {device_id}")

    db = TinyDB("database/beacons.json")
    query = Query()
    result = db.search(query.deviceId == device_id)

    if not result:
        return jsonify(success=False, message="Device not found."), 404

    device_info = result[0]

    print(f"Get device info request from user: {request.user} for device ID: {device_id}")
    return jsonify(success=True, data=device_info), 200


# Get the messages from the Beacon device
#   -- optionally 'deviceId' and 'since' can be provided in the request body
@app.route("/get-messages", methods=["GET"])
@token_required
def get_messages():
    device_id = request.args.get('deviceId')
    since = request.args.get('since')

    db = TinyDB("database/messages.json")
    Message = Query()

    query = None

    if device_id:
        q = (Message.deviceId == device_id)
        query = q if query is None else query & q

    if since:
        q = (Message.timestamp >= since)
        query = q if query is None else query & q

    if query is None:
        results = db.all()
    else:
        results = db.search(query)

    print(f"Get messages by user: {request.user} from device ID: {device_id}")
    return jsonify(success=True, data=results), 200


# Get the images from the Beacon device
@app.route("/get-images", methods=["GET"])
@token_required
def get_images():
    device_id = request.args.get('deviceId')

    print(f"Get images by user: {request.user} from device ID: {device_id}")

    image_path = f"./uploads/beacon_image.png"

    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return jsonify(success=False, message="Image not found"), 404

    return send_file(image_path, mimetype='image/jpeg')



#######################################
#
#   Beacon API Endpoints
#
#######################################


# Send message from the Beacon device
#   -- requires 'message' and 'deviceId' in the request body
@app.route("/send-message", methods=["POST"])
@token_required
def send_message():
    data = request.json or {}

    if not 'message' in data or not 'deviceId' in data:
        return jsonify(success=False, message="Message text and Device ID are required."), 400

    db = TinyDB("database/messages.json")
    db.insert({"message": data["message"], "deviceId": data["deviceId"], "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()})

    DeviceManager.UpdateBeaconData(data["deviceId"])

    print(f"Send message by user: {request.user} with message: {data['message']}")
    return jsonify(success=True, message=f"Message sent successfully."), 200


# Send image from the Beacon device
@app.route("/send-image", methods=["POST"])
@token_required
def send_image():
    data = request.json or {}
    image = data.get('image')
    if not image:
        return jsonify(success=False, message="Image and Device ID are required."), 400

    try:
        # If the image is in base64 format, e.g. "data:image/png;base64,...."
        if "," in image:
            header, image = image.split(",", 1)

        # Decoding
        image_bytes = base64.b64decode(image)

        # Save location (e.g. "uploads" folder)
        os.makedirs("uploads", exist_ok=True)
        filename = f"uploads/{request.user}_image.png"

        with open(filename, "wb") as f:
            f.write(image_bytes)

        
        print(f"Send arrived from user: {request.user}, saved to: {filename}")
        return jsonify(success=True, message=f"Picture uploaded successfully: {filename}"), 200

    except Exception as e:
        return jsonify(success=False, message=f"Error occurred: {e}"), 500




# Send info from the Beacon device
#   -- requires 'deviceId' and at least one of 'batteryLevel', 'controllerBattery', 'coreTemp', or 'houseTemp' in the request body
@app.route("/send-info", methods=["POST"])
@token_required
def send_info():
    data = request.json or {}

    if not 'deviceId' in data:
        return jsonify(success=False, message="Device ID is missing"), 400

    deviceId = data.get('deviceId')
    batteryLevel = data.get('batteryLevel') or None
    coreTemp = data.get('coreTemp') or None
    houseTemp = data.get('houseTemp') or None
    controllerBattery = data.get('controllerBattery') or None

    DeviceManager.UpdateBeaconData(deviceId, batteryLevel=batteryLevel, controllerBattery=controllerBattery, coreTemp=coreTemp, houseTemp=houseTemp)

    print(f"Beacon data is updated for device ID: {deviceId}.")

    return jsonify(success=True, message=f"Device {deviceId} updated successfully."), 200


#######################################
#
#   Beacon Configuration Endpoints (client side)
#
#######################################


# Configure the Beacon's camera
@app.route("/configure-camera", methods=["POST"])
@token_required
def configure_camera():
    data = request.json or {}
    DeviceManager.UpdateCameraConfiguration(data)
    print(f"Configure camera by: {request.user}: {data}")
    return jsonify(success=True, message=f"Camera configured successfully."), 200


# Configure the Beacon
@app.route("/configure-beacon", methods=["POST"])
@token_required
def configure_beacon():
    data = request.json or {}
    config = data.get('config')
    print(f"Configure beacon by user: {request.user} with config: {config}")
    return jsonify(success=True, message=f"Hello {request.user}, beacon configured successfully."), 200


#######################################
#
#   Beacon Configuration Endpoints (Beacon side)
#
#######################################


# Get the Beacon's configuration
@app.route("/get-beacon-configuration", methods=["GET"])
@token_required
def get_beacon_configuration():
    print(f"Get beacon configuration by user: {request.user}")
    return jsonify(success=True, message=f"Hello {request.user}, get beacon configuration successful."), 200


# Get the Beacon's camera configuration
@app.route("/get-camera-configuration", methods=["GET"])
@token_required
def get_camera_configuration():
    with open("database/camera-config.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Camera configuration by: {request.user}")
    return jsonify(success=True, data=data), 200


if __name__ == "__main__":
    with open("database/server-config.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if data['server'].get('log_to_file', False):
        logging.basicConfig(filename=data['server']['log_file'], level=logging.INFO)

    app.config['SECRET_KEY'] = data['server']['secret_key']  # Reading the secret key from the config file
    app.run(host=data['server']['host'], port=data['server']['port'], debug=data['server']['debug'], threaded=True)
