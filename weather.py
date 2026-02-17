import requests
import json
import os
from datetime import datetime
from twilio.rest import Client

# --- CONFIG FROM ENVIRONMENT ---
API_KEY = os.getenv("OPENWEATHER_KEY")
LAT = os.getenv("LAT")
LON = os.getenv("LON")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
FROM_NUMBER = os.getenv("FROM_NUMBER")
TO_NUMBER = os.getenv("TO_NUMBER")

WAKE_HOUR = 6
SLEEP_HOUR = 21
STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"rain_alert_sent": False, "last_alert_id": None, "tomorrow_sent_date": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=imperial"
    response = requests.get(url)
    return response.json()


def send_text(message):
    print("Sending WhatsApp message...")
    client = Client(TWILIO_SID, TWILIO_AUTH)
    msg = client.messages.create(
        body=message,
        from_="whatsapp:+14155238886",
        to=f"whatsapp:{TO_NUMBER}"
    )
    print("Message SID:", msg.sid)


def run():
    print("Running weather script...")

    data = get_weather()
    print("FULL API RESPONSE:")
    print(data)

    return



if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("Error:", e)
