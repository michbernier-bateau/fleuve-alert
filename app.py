import requests
import time
import math
import os

# ====== CONFIGURATION ======
LATITUDE = 46.61480
LONGITUDE = -71.94333
RADIUS_KM = 1

PUSHOVER_USER = os.getenv("PUSHOVER_USER")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")

CHECK_INTERVAL = 300  # 5 minutes

seen_vessels = set()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def send_notification(message):
    requests.post("https://api.pushover.net/1/messages.json", data={
        "token": PUSHOVER_TOKEN,
        "user": PUSHOVER_USER,
        "message": message
    })

def get_vessels():
    # Source AIS publique gratuite (peut être instable)
    url = "https://aisstream.io/v0/stream"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return []

while True:
    vessels = get_vessels()

    for vessel in vessels:
        try:
            lat = vessel.get("lat")
            lon = vessel.get("lon")
            name = vessel.get("name", "Navire inconnu")

            if lat and lon:
                distance = haversine(LATITUDE, LONGITUDE, lat, lon)
                if distance <= RADIUS_KM:
                    vessel_id = vessel.get("mmsi")

                    if vessel_id not in seen_vessels:
                        seen_vessels.add(vessel_id)
                        send_notification(f"🚢 {name} passe devant chez vous.")
        except:
            continue

    time.sleep(CHECK_INTERVAL)
