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
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&appid={API_KEY}&units=imperial"
    return requests.get(url).json()

def send_text(message):
    print("Attempting to send SMS...")
    client = Client(TWILIO_SID, TWILIO_AUTH)
    msg = client.messages.create(
        body=message,
        from_=FROM_NUMBER,
        to=TO_NUMBER
    )
    print("Message SID:", msg.sid)


def run():
    send_text("Test message from GitHub Actions")
    return

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    hour = now.hour

    state = load_state()
    data = get_weather()

    current_temp = round(data["current"]["temp"])
    current_desc = data["current"]["weather"][0]["description"].title()

    # Hourly update
    if WAKE_HOUR <= hour <= SLEEP_HOUR:
        message = f"{now.strftime('%I:%M %p')} Weather:\n{current_temp}°F — {current_desc}"
        send_text(message)

    # Rain/Snow alert
    rain_expected = False
    for hour_data in data["hourly"][:3]:
        desc = hour_data["weather"][0]["description"].lower()
        if "rain" in desc or "snow" in desc:
            rain_expected = True
            break

    if rain_expected and not state["rain_alert_sent"]:
        send_text("⚠️ Rain or snow expected soon.")
        state["rain_alert_sent"] = True

    if not rain_expected:
        state["rain_alert_sent"] = False

    # Severe alerts
    if "alerts" in data:
        for alert in data["alerts"]:
            alert_id = alert.get("event") + str(alert.get("start"))
            if alert_id != state["last_alert_id"]:
                send_text(f"🚨 WEATHER ALERT:\n{alert['event']}")
                state["last_alert_id"] = alert_id

    # Tomorrow forecast at 8 PM
    if hour == 20 and state["tomorrow_sent_date"] != today_str:
        tomorrow = data["daily"][1]
        high = round(tomorrow["temp"]["max"])
        low = round(tomorrow["temp"]["min"])
        desc = tomorrow["weather"][0]["description"].title()

        send_text(f"🌤 Tomorrow:\nHigh {high}°F / Low {low}°F\n{desc}")
        state["tomorrow_sent_date"] = today_str

    save_state(state)

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("Error:", e)
