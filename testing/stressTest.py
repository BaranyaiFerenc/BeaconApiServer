from locust import HttpUser, task, between
import json
import random

class BeaconUser(HttpUser):
    wait_time = between(1, 3)  # 1-3 másodperc várakozás két request között

    def on_start(self):
        """
        Minden user indulásakor lefut: bejelentkezés és token eltárolása.
        """
        payload = {
            "username": "admin",   # <-- állítsd be valós user/passra
            "password": "Titok123"
        }
        with self.client.post("/login", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                token = response.json().get("access_token")
                self.client.headers = {
                    "Authorization": f"Bearer {token}"
                }
            else:
                response.failure("Login failed")

    @task(3)
    def ping(self):
        self.client.get("/ping")

    @task(2)
    def get_devices(self):
        self.client.get("/get-devices")

    @task(2)
    def get_messages(self):
        # random deviceId (ha nincs, akkor simán csak hívja az endpointot)
        device_id = random.choice(["device1", "device2", "device3"])
        self.client.get(f"/get-messages?deviceId={device_id}")

    @task(1)
    def send_message(self):
        payload = {
            "deviceId": "device1",
            "message": f"stress-test-{random.randint(1,1000)}"
        }
        self.client.post("/send-message", json=payload)
