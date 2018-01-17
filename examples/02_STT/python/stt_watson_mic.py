# Example STT - "watson streaming"
# Modified example from "ibm-dev/watson-streaming-stt"

import os
import sys
import base64
import json
import pyaudio
import time
import websocket
from websocket._abnf import ABNF
try:
    import thread
except ImportError:
    import _thread as thread

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 15
FINALS = []

def listen(ws, timeout):
    global RATE
    p = pyaudio.PyAudio()
    # input_device_index=N,
    RATE = int(p.get_default_input_device_info()['defaultSampleRate'])
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* rec")
    rec = timeout or RECORD_SECONDS

    for i in range(0, int(RATE / CHUNK * rec)):
        data = stream.read(CHUNK)
        ws.send(data, ABNF.OPCODE_BINARY)

    # Disconnect the audio stream
    stream.stop_stream()
    stream.close()
    print(u"\u2588" + " stop")

    # In order to get a final response from STT we send a stop, this
    # will force a final=True return message.
    data = {"action": "stop"}
    ws.send(json.dumps(data).encode('utf8'))
    # ... which we need to wait for before we shutdown the websocket
    time.sleep(1)
    ws.close()

    # ... and kill the audio device
    p.terminate()


def on_message(ws, message):
    data = json.loads(message)
    if "results" in data:
        print(data['results'][0]['alternatives'][0]['transcript'])
        done = {"action": "stop"}
        ws.send(json.dumps(done).encode('utf8'))

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    timeout = 10
    settings = {
        "action": "start",
        "content-type": "audio/l16;rate=%d" % RATE,
        # "continuous": True,
        "interim_results": False,
        "word_confidence": True,
        "timestamps": True,
        "max_alternatives": 3
    }
    ws.send(json.dumps(settings).encode('utf8'))
    thread.start_new_thread(listen,(ws,timeout))


def connect():
    # websocket.enableTrace(True)
    user = "9e0a3437-aa25-4a21-87e0-20fb1d02db63"
    password = "UPu8SOsrz8eX"
    url = 'wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize?model=en-US_BroadbandModel'
    headers = {}
    auth = user + ":" + password
    headers["Authorization"] = "Basic " + base64.b64encode(
        auth.encode()).decode()

    ws = websocket.WebSocketApp(url,
                              header=headers,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)

    ws.on_open = on_open
    ws.run_forever()


connect()
