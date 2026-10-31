import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
# These absolute imports work when running from the root folder
from src.triage_engine import TriageEngine
from src.geo_database import GeoDatabase

app = FastAPI()

# 1. Define the SOSRequest blueprint (Fixes the NameError)
class SOSRequest(BaseModel):
    message: str
    lat: float
    lng: float

# 2. Mount the static folder so we can see the UI
# This assumes you have a folder named 'static' in your root directory
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. Initialize our Brain and Compass
engine = TriageEngine()
db = GeoDatabase()

# 4. Route to serve the HTML Dashboard
@app.get("/")
def home():
    return FileResponse("static/index.html")

# Health check for uptime monitoring (keeps the free Render instance awake)
@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}

# 5. The Core SOS logic
@app.post("/sos")
def handle_sos(request: SOSRequest):
    # Ask the AI Brain to analyze the message
    data = engine.analyze(request.message)
    
    # Ask the Database Compass to find hospitals based on severity
    hospitals = db.get_nearest_facilities(request.lat, request.lng, data["severity"])
    
    if not hospitals:
        return {
            "bot_response": "🚨 NO TRAUMA CENTERS FOUND NEARBY. CALL 1669/112 IMMEDIATELY.",
            "severity": data["severity"],
            "metadata": data
        }
        
    h = hospitals[0]
    return {
        "bot_response": f"🚨 Help Alerted. Nearest Trauma: {h['name']} ({round(h['dist'], 2)}km). Call: {h['phone_primary']}",
        "severity": data["severity"],
        "metadata": data
    }