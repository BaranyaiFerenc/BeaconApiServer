import asyncio
import json
import sounddevice as sd
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaStreamTrack
from aiohttp import ClientSession, WSMsgType, TCPConnector

SIGNAL_URL = "wss://localhost:5000/ws"  # ha SSL, akkor wss://
SELF_ID = "python-listener"
TARGET_ID = "python-sender"

async def main():
    connector = TCPConnector(ssl=False)
    async with ClientSession(connector=connector) as session:
        async with session.ws_connect(SIGNAL_URL) as ws:
            await ws.send_str(SELF_ID)
            print("[WS] connected")

            pc = RTCPeerConnection()

            @pc.on("track")
            async def on_track(track: MediaStreamTrack):
                print("[PC] got track:", track.kind)
                if track.kind != "audio":
                    return

                # valós idejű lejátszás
                async def play_audio():
                    while True:
                        frame = await track.recv()
                        # PCM float32 tömb
                        samples = frame.to_ndarray()
                        # sounddevice: channel-ok T, samplerate
                        sd.play(samples.T, samplerate=frame.sample_rate, blocking=True)

                asyncio.create_task(play_audio())

            async for msg in ws:
                if msg.type != WSMsgType.TEXT:
                    continue
                data = json.loads(msg.data)
                if data.get("type") == "offer" and data.get("target") == SELF_ID:
                    offer = RTCSessionDescription(sdp=data["sdp"], type="offer")
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
