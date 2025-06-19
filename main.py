from fastapi import FastAPI
from pydantic import BaseModel
import swisseph as swe
import datetime
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from typing import Optional

app = FastAPI()

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

def get_coordinates(location_name):
    geolocator = Nominatim(user_agent="panchanga_calculator")
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    return None, None

def get_timezone_for_coordinates(lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon)
    return tz_name if tz_name else 'UTC'

def calculate_sunrise(date, lat, lon, timezone):
    jd = swe.julday(date.year, date.month, date.day, 0.0)
    rsmi = swe.CALC_RISE | swe.BIT_DISC_CENTER
    geopos = [lon, lat, 0.0]
    result = swe.rise_trans(jd, swe.SUN, rsmi, geopos, 0.0, 10.0, swe.FLG_MOSEPH)
    if result[0] == 0:
        sunrise_jd = result[1][0]
        year, month, day, hour = swe.revjul(sunrise_jd)
        hour_int = int(hour)
        minute_int = int((hour - hour_int) * 60)
        second_int = int((((hour - hour_int) * 60) - minute_int) * 60)
        sunrise_utc = datetime.datetime(year, month, day, hour_int, minute_int, second_int, tzinfo=pytz.UTC)
        return sunrise_utc.astimezone(timezone)
    return None

def calculate_longitudes(jd):
    sun = swe.calc_ut(jd, swe.SUN, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)[0][0]
    moon = swe.calc_ut(jd, swe.MOON, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)[0][0]
    return sun, moon

def calculate_panchanga_elements(date_time):
    jd = swe.julday(date_time.year, date_time.month, date_time.day,
                    date_time.hour + date_time.minute/60.0 + date_time.second/3600.0)
    sun, moon = calculate_longitudes(jd)
    tithi_angle = (moon - sun) % 360
    tithi_num = int(tithi_angle / 12) + 1
    nakshatra_num = int(moon / (360/27)) + 1
    yoga_num = int(((sun + moon) % 360) / (360/27)) + 1
    karana_num = int((tithi_angle / 2) / 6) + 1
    return {
        'tithi': (tithi_num, TITHIS[(tithi_num - 1) % 30]),
        'nakshatra': (nakshatra_num, NAKSHATRAS[(nakshatra_num - 1) % 27]),
        'yoga': (yoga_num, YOGAS[(yoga_num - 1) % 27]),
        'karana': (karana_num, KARANAS[(karana_num - 1) % 11])
    }

def check_eclipse(jd):
    lunar = swe.lun_eclipse_when(jd, swe.FLG_MOSEPH)[1]
    solar = swe.sol_eclipse_when_glob(jd, swe.FLG_MOSEPH)[1]
    lunar_date = lunar[0] if lunar else None
    solar_date = solar[0] if solar else None
    return lunar_date, solar_date

def travel_risk_level(panchanga, weekday, jd):
    risk_factors = 0
    if panchanga['tithi'][0] in MALEFIC_TITHIS:
        risk_factors += 1
    if panchanga['nakshatra'][0] in MALEFIC_NAKSHATRAS:
        risk_factors += 1
    if panchanga['yoga'][0] in MALEFIC_YOGAS:
        risk_factors += 1
    if panchanga['karana'][0] in MALEFIC_KARANAS:
        risk_factors += 1
    if weekday == 1:
        risk_factors += 1
    lunar, solar = check_eclipse(jd)
    if lunar and abs(lunar - jd) < 1:
        risk_factors += 3
    if solar and abs(solar - jd) < 1:
        risk_factors += 3
    if risk_factors >= 3:
        return "Extreme Risk"
    elif risk_factors == 2:
        return "High Risk"
    elif risk_factors == 1:
        return "Caution"
    else:
        return "Safe"

@app.post("/panchanga")
def get_panchanga(data: PanchangaRequest):
    location = f"{data.city}, {data.country}"
    lat, lon = get_coordinates(location)
    if not lat:
        return {"error": "Location not found"}

    tz_name = get_timezone_for_coordinates(lat, lon)
    timezone = pytz.timezone(tz_name)

    now = datetime.datetime.now(timezone)
    user_datetime = now

    if data.date:
        try:
            date_part = datetime.datetime.strptime(data.date, "%Y-%m-%d")
            hour = 0
            minute = 0
            if data.time:
                t = datetime.datetime.strptime(data.time, "%H:%M")
                hour, minute = t.hour, t.minute
            user_datetime = timezone.localize(datetime.datetime(date_part.year, date_part.month, date_part.day, hour, minute))
        except:
            return {"error": "Invalid date/time format"}

    actual_panchanga = calculate_panchanga_elements(user_datetime)

    forecast = []
    for i in range(data.days):
        target_date = now + datetime.timedelta(days=i)
        sunrise = calculate_sunrise(target_date, lat, lon, timezone)
        if not sunrise:
            continue
        panchanga = calculate_panchanga_elements(sunrise)
        jd = swe.julday(target_date.year, target_date.month, target_date.day, 0)
        lunar, solar = check_eclipse(jd)
        eclipse = "Lunar Eclipse" if lunar and abs(lunar - jd) < 1 else (
            "Solar Eclipse" if solar and abs(solar - jd) < 1 else "No Eclipse")
        risk = travel_risk_level(panchanga, target_date.weekday(), jd)
        disha_shool = DISHA_SHOOL[target_date.weekday()]

        forecast.append({
            "date": target_date.strftime("%Y-%m-%d"),
            "sunrise": sunrise.strftime('%H:%M:%S %Z'),
            "tithi": panchanga['tithi'][1],
            "nakshatra": panchanga['nakshatra'][1],
            "yoga": panchanga['yoga'][1],
            "karana": panchanga['karana'][1],
            "eclipse": eclipse,
            "risk": risk,
            "remedy": REMEDIES[risk],
            "disha_shool": disha_shool
        })

    return {
        "location": location,
        "actual_now": {
            "datetime": user_datetime.strftime("%Y-%m-%d %H:%M"),
            "tithi": actual_panchanga['tithi'][1],
            "nakshatra": actual_panchanga['nakshatra'][1],
            "yoga": actual_panchanga['yoga'][1],
            "karana": actual_panchanga['karana'][1]
        },
        "forecast": forecast
    }
