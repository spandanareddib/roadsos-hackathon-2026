# geo_database.py (The Compass)
# This only handles hospital searching.

import json
from math import radians, cos, sin, asin, sqrt

class GeoDatabase:
    def __init__(self):
        # Path changed to data/ folder
        with open("data/mock_db.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)["facilities"]

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371
        dLat, dLon = radians(lat2-lat1), radians(lon2-lon1)
        a = sin(dLat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dLon/2)**2
        return R * 2 * asin(sqrt(a))

    def get_nearest_facilities(self, lat, lng, severity):
        eligible = []
        for f in self.data:
            if severity >= 5 and not f.get("has_blood_bank"): continue
            if severity >= 3 and f["facility_type"] == "clinic": continue
            f["dist"] = self.haversine(lat, lng, f["latitude"], f["longitude"])
            eligible.append(f)
        return sorted(eligible, key=lambda x: x["dist"])[:2]