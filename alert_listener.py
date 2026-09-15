import json
import paho.mqtt.subscribe as subscribe

def on_message(client, userdata, msg):
    alert = json.loads(msg.payload.decode())
    print("")
    print("* ALERT *")
    for k, v in alert.items():
        print("  ", k, ":", v)

print("Listening for alerts on sentinel/alerts ...")
subscribe.callback(on_message, "sentinel/alerts", hostname="localhost", port=1883)
