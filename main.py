from fastapi import FastAPI
from pydantic import BaseModel
import swisseph as swe
import datetime
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from typing import Optional

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to Vedic Panchanga API. Use POST /panchanga for results."}

# Constants
TITHIS = [
    "Shukla Pratipada", "Shukla Dwitiya", "Shukla Tritiya", "Shukla Chaturthi", "Shukla Panchami",
    "Shukla Shashti", "Shukla Saptami", "Shukla Ashtami", "Shukla Navami", "Shukla Dashami",
    "Shukla Ekadashi", "Shukla Dwadashi", "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima",
    "Krishna Pratipada", "Krishna Dwitiya", "Krishna Tritiya", "Krishna Chaturthi", "Krishna Panchami",
    "Krishna Shashti", "Krishna Saptami", "Krishna Ashtami", "Krishna Navami", "Krishna Dashami",
    "Krishna Ekadashi", "Krishna Dwadashi", "Krishna Trayodashi", "Krishna Chaturdashi", "Amavasya"
]
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]
YOGAS = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarman",
    "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha",
    "Shukla", "Brahma", "Indra", "Vaidhriti"
]
KARANAS = [
    "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
    "Shakuni", "Chatushpada", "Naga", "Kimstughna"
]

MALEFIC_TITHIS = {23, 29, 30}
MALEFIC_NAKSHATRAS = {2, 5, 8, 10, 13, 18, 19, 26}
MALEFIC_YOGAS = {17, 27, 19}
MALEFIC_KARANAS = {7}

REMEDIES = {
    "Extreme Risk": "Avoid journey. If unavoidable, recite Hanuman Chalisa and donate black sesame.",
    "High Risk": "Postpone journey if possible. Light a ghee lamp before Hanuman ji.",
    "Caution": "Chant 'Om Namo Narayanaya' 108 times before travel.",
    "Safe": "No remedy needed. Proceed with confidence."
}

DISHA_SHOOL = {
    0: "East",
    1: "North",
    2: "North",
    3: "West",
    4: "South",
    5: "South",
    6: "West"
}

swe.set_ephe_path(".")
swe.set_sid_mode(swe.SIDM_LAHIRI)

class PanchangaRequest(BaseModel):
    city: str
    country: str
    days: int
    date: Optional[str] = None
    time: Optional[str] = None

# ... rest of the unchanged code remains the same
