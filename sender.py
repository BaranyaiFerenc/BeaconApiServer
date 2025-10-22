import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer
from aiohttp import ClientSession, WSMsgType, TCPConnector

SIGNAL_URL = "wss://127.0.0.1:5000/ws"  # Szerver IP/port
SELF_ID = "python-sender"
TARGET_ID = "python-listener"

async def main():
    connector = TCPConnector(ssl=False)
    async with ClientSession(connector=connector) as session:
        async with session.ws_connect(SIGNAL_URL) as ws:
            await ws.send_str(SELF_ID)
            print("[WS] connected")

            pc = RTCPeerConnection()

            # --- Windows mikrofon capture ---
            # Ellenőrizd a mikrofon nevét a "Sound settings -> Recording devices"-n
            player = MediaPlayer(
                'audio=Mikrofon (C-Media(R) Audio)',
                format='dshow'
            )
            pc.addTrack(player.audio)

            # --- Signaling ---
            async def signaling():
                # Offer készítése
                offer = await pc.createOffer()
                await pc.setLocalDescription(offer)

                # Offer küldése a signaling szervernek
                await ws.send_str(json.dumps({
                    "type": "offer",
                    "from": SELF_ID,
                    "target": TARGET_ID,
                    "sdp": pc.localDescription.sdp
                }))
                print("[SIG] offer sent")

                async for msg in ws:
                    if msg.type != WSMsgType.TEXT:
                        continue
                    data = json.loads(msg.data)

                    # Answer fogadása
                    if data.get("type") == "answer" and data.get("target") == SELF_ID:
                        answer = RTCSessionDescription(
                            sdp=data["sdp"],
                            type=data["type"]
                        )
                        await pc.setRemoteDescription(answer)
                        print("[SIG] answer received")

            await signaling()

asyncio.run(main())
