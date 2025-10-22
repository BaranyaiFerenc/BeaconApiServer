import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRecorder
from aiohttp import ClientSession, WSMsgType, TCPConnector

SIGNAL_URL = "wss://localhost:5000/ws"  # ha SSL, akkor wss://
SELF_ID = "python-listener"
TARGET_ID = "python-sender"

async def main():
    connector = TCPConnector(ssl=False)
    async with ClientSession(connector=connector) as session:
        async with session.ws_connect(SIGNAL_URL) as ws:
            # Peer ID elküldése
            await ws.send_str(SELF_ID)
            print("[WS] connected")

            pc = RTCPeerConnection()
            # Hangot WAV fájlba menti
            recorder = MediaRecorder("output.wav")

            @pc.on("track")
            async def on_track(track):
                print("[PC] got track:", track.kind)
                if track.kind == "audio":
                    recorder.addTrack(track)
                    await recorder.start()

            # WebSocket üzenetek kezelése
            async for msg in ws:
                if msg.type != WSMsgType.TEXT:
                    continue
                data = json.loads(msg.data)

                # Ha offer érkezik
                if data.get("type") == "offer" and data.get("target") == SELF_ID:
                    offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                    await pc.setRemoteDescription(offer)

                    answer = await pc.createAnswer()
                    await pc.setLocalDescription(answer)

                    await ws.send_str(json.dumps({
                        "type": "answer",
                        "from": SELF_ID,
                        "target": TARGET_ID,
                        "sdp": pc.localDescription.sdp
                    }))
                    print("[SIG] answer sent")

asyncio.run(main())
