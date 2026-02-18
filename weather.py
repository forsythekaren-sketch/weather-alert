import pytz
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

    recipients = [
        f"whatsapp:{TO_NUMBER}",
        f"whatsapp:{os.getenv('TO_NUMBER_2')}"
    ]

    for recipient in recipients:
        msg = client.messages.create(
            body=message,
            from_="whatsapp:+14155238886",
            to=recipient
        )
        print("Sent to", recipient, "SID:", msg.sid)

def run():
    print("Running weather script...")

    eastern = pytz.timezone("America/New_York")
    now = datetime.now(eastern)

    hour = now.hour

    data = get_weather()

    current_temp = round(data["main"]["temp"])
    current_desc = data["weather"][0]["description"].title()
    wind_speed = data["wind"]["speed"]

    message_parts = []

    # 1️⃣ Hourly updates between 6 AM–9 PM
    if True:
        message_parts.append(f"{current_temp}°F — {current_desc}")

    # 2️⃣ Rain / Snow detection
    desc_lower = current_desc.lower()
    if "rain" in desc_lower:
        message_parts.append("🌧 Rain detected.")
    if "snow" in desc_lower:
        message_parts.append("❄️ Snow detected.")

    # 3️⃣ Wind advisory approximation
    if wind_speed >= 25:
        message_parts.append(f"💨 High winds: {wind_speed} mph")

    # 4️⃣ Tomorrow forecast at 8 PM
    if hour == 20:
        forecast = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=imperial"
        ).json()

        tomorrow = forecast["list"][8]  # ~24 hours ahead (3hr intervals)
        high = round(tomorrow["main"]["temp"])
        desc = tomorrow["weather"][0]["description"].title()

        message_parts.append(f"🌤 Tomorrow: {high}°F — {desc}")

    if message_parts:
        final_message = "\n".join(message_parts)
        send_text(final_message)
        print("Message sent.")
    else:
        print("No conditions met. No message sent.")



if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("Error:", e)
