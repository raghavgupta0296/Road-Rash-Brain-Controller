import threading
import time
from pynput import keyboard
import websocket
import _thread
import json
import ssl
import numpy as np
import pickle

auth_key = ""
values = []
current_keys = set()
is_esc = False
key_mapped_values = {i: [] for i in ["up-left", "up-right", "down-left", "down-right", "up", "down", "left", "right", "space", "enter"]}
key_values_seq = ""
key_pressed = ""


def on_press(key):
    global current_keys
    global key_pressed
    global key_mapped_values
    global key_values_seq
    current_keys.add(key)

    if len(current_keys)>0:
        key_pressed = ""
        if keyboard.Key.up in current_keys:
            if keyboard.Key.left in current_keys:
                key_pressed = "up-left"
            elif keyboard.Key.right in current_keys:
                key_pressed = "up-right"
            else:
                key_pressed = "up"
        elif keyboard.Key.down in current_keys:
            if keyboard.Key.left in current_keys:
                key_pressed = "down-left"
            elif keyboard.Key.right in current_keys:
                key_pressed = "down-right"
            else:
                key_pressed = "down"
        elif keyboard.Key.left in current_keys:
            key_pressed = "left"
        elif keyboard.Key.right in current_keys:
            key_pressed = "right"
        if keyboard.Key.space in current_keys:
            key_pressed = "space"
        if keyboard.Key.enter in current_keys:
            key_pressed = "enter"
        print(key_pressed)
        # print(key_mapped_values)
        # print(values)
        try:
            key_mapped_values[key_pressed].append(values)
            key_values_seq += key_pressed + str(values) + "\n"
        except Exception as e:
            print("error", e)
        # print(key_mapped_values)


def on_release(key):
    global current_keys
    global is_esc

    current_keys.remove(key)
    if key == keyboard.Key.esc:
        print("true")
        is_esc = True
        save_vals()
        return False  # Stop listener


# ids -1: login, 0: auth, 1: headset search, 2: create session, 3: close session, 4: gyro info, 5: close gyro info


def readEmotiv(ws):
    global auth_key
    while auth_key == "":
        pass
    print("#" * 10, "Authorized through", auth_key)

    payload = {
        "jsonrpc": "2.0",
        "method": "queryHeadsets",
        "params": {},
        "id": 1
    }
    ws.send(json.dumps(payload))

    payload = {
        "jsonrpc": "2.0",
        "method": "createSession",
        "params": {
            "_auth": auth_key,
            "status": "open",
            "headset": "EPOCPLUS-3B9AE2E6"
        },
        "id": 2
    }
    ws.send(json.dumps(payload))

    payload = {
        "jsonrpc": "2.0",
        "method": "subscribe",
        "params": {
            "_auth": auth_key,
            "streams": [
                "pow"
            ]
        },
        "id": 4
    }
    ws.send(json.dumps(payload))


def on_open(ws):
    print("on_open")
    print("#" * 10, "Connected to headset")
    payload = {
        "jsonrpc": "2.0",
        "method": "getUserLogin",
        "id": -1
    }
    ws.send(json.dumps(payload))
    print("sending login info")

    payload = {
        "jsonrpc": "2.0",
        "method": "authorize",
        "params": {},
        "id": 0
    }
    ws.send(json.dumps(payload))
    # print("sending authorization req")

    _thread.start_new_thread(readEmotiv, (ws,))


def on_message(ws, message):
    global auth_key
    global values

    message = json.loads(message)
    try:
        if message["id"] == 0:
            auth_key = message["result"]["_auth"]
        print("!" * 5, "on_message", message)
    except:
        if message["pow"]:
            # print("!" * 5, "on_data", message)
            values = np.array(message["pow"])
            # print(key_pressed, values)
            # print(is_esc)
            if is_esc:
                return False


def on_error(ws, error):
    print("on_error")
    print(error)


def on_close(ws):
    payload = {
        "jsonrpc": "2.0",
        "method": "unsubscribe",
        "params": {
            "_auth": auth_key,
            "streams": [
                "pow"
            ]
        },
        "id": 5
    }
    ws.send(json.dumps(payload))

    payload = {
        "jsonrpc": "2.0",
        "method": "updateSession",
        "params": {
            "_auth": auth_key,
            "status": "close"
        },
        "id": 3
    }
    ws.send(json.dumps(payload))

    ws.close()
    print("on_close")


def save_vals():
    with open("dataset.pkl","wb") as f:
        pickle.dump(key_mapped_values, f)
    with open("dataseq.txt","w") as g:
        g.write(key_values_seq)


def epochInput():
    ws = websocket.WebSocketApp("wss://emotivcortex.com:54321", on_message=on_message, on_close=on_close,
                                on_error=on_error,
                                on_open=on_open, )

    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    ws.close()


listener = keyboard.Listener(on_press=on_press, on_release=on_release)

listener.start()

epochInput()
listener.join()

print("!!!! Finished Recording ")

for i in key_mapped_values.keys():
    print(i, len(key_mapped_values[i]))
