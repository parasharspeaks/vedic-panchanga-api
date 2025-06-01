import swisseph as swe
import datetime
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim

# Initialize Swiss Ephemeris
swe.set_ephe_path(".")
swe.set_sid_mode(swe.SIDM_LAHIRI)

TITHIS = [
    "Shukla Pratipada", "Shukla Dwitiya", "Shukla Tritiya", "Shukla Chaturthi", "Shukla Panchami",
    "Shukla Shashti", "Shukla Saptami", "Shukla Ashtami", "Shukla Navami", "Shukla Dashami",
    "Shukla Ekadashi", "Shukla Dwadashi", "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima",
    "Krishna Pratipada", "Krishna Dwitiya", "Krishna Tritiya", "Krishna Chaturthi", "Krishna Panchami",
    "Krishna Shashti", "Krishna Saptami", "Krishna Ashtami", "Krishna Navami", "Krishna Dashami",
    "Krishna Ekadashi", "Krishna Dwadashi", "Krishna Trayodashi", "Krishna Chaturdashi", "Amavasya"]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"]

YOGAS = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarman",
    "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha",
    "Shukla", "Brahma", "Indra", "Vaidhriti"]

KARANAS = [
    "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
    "Shakuni", "Chatushpada", "Naga", "Kimstughna"]

# Malefic sets
MALEFIC_TITHIS = {23, 29, 30}
MALEFIC_NAKSHATRAS = {2, 5, 8, 10, 13, 18, 19, 26}
MALEFIC_YOGAS = {17, 27, 19}
MALEFIC_KARANAS = {7}

def get_coordinates(location_name):
    geolocator = Nominatim(user_agent="panchanga_calculator")
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

def get_timezone_for_coordinates(lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon)
    return tz_name if tz_name else 'UTC'

def calculate_sunrise(date, lat, lon, timezone):
    date_utc = date.astimezone(pytz.UTC)
    jd = swe.julday(date_utc.year, date_utc.month, date_utc.day, 0.0)
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

def calculate_panchanga_elements(date_time, timezone):
    date_utc = date_time.astimezone(pytz.UTC)
    jd = swe.julday(date_utc.year, date_utc.month, date_utc.day,
                    date_utc.hour + date_utc.minute/60.0 + date_utc.second/3600.0)
    
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

def main():
    import sys
    for attempt in range(2):
        location = input("Enter city and country (e.g., 'Mumbai, India'): ")
        lat, lon = get_coordinates(location)
        if lat is not None:
            break
        else:
            print("Location not found. Please enter a valid location.")
    else:
        print("Bad input.")
        sys.exit(1)

    tz_name = get_timezone_for_coordinates(lat, lon)
    timezone = pytz.timezone(tz_name)

    for attempt in range(2):
        date_input = input("Enter start date (YYYY-MM-DD): ")
        try:
            date = datetime.datetime.strptime(date_input, "%Y-%m-%d")
            date = timezone.localize(date)
            break
        except ValueError:
            print("Invalid date format. Please enter date in YYYY-MM-DD format.")
    else:
        print("Bad input.")
        sys.exit(1)

    for attempt in range(2):
        try:
            forecast_days = int(input("Enter number of forecast days (max 30): "))
            if 1 <= forecast_days <= 30:
                break
            else:
                print("Forecast days must be between 1 and 30.")
        except:
            print("Invalid forecast days input. Please enter an integer.")
    else:
        print("Bad input.")
        sys.exit(1)

    for i in range(forecast_days):
        target_date = date + datetime.timedelta(days=i)
        sunrise = calculate_sunrise(target_date, lat, lon, timezone)
        if sunrise is None:
            print("Could not calculate sunrise for:", target_date.strftime("%Y-%m-%d"))
            continue
        panchanga = calculate_panchanga_elements(sunrise, timezone)
        jd = swe.julday(target_date.year, target_date.month, target_date.day, 0)

        print("\nPanchanga for", location, "on", target_date.strftime("%Y-%m-%d"))
        print("Sunrise:", sunrise.strftime('%H:%M:%S %Z'))
        print(f"Tithi: {panchanga['tithi'][1]} (#{panchanga['tithi'][0]})")
        print(f"Nakshatra: {panchanga['nakshatra'][1]} (#{panchanga['nakshatra'][0]})")
        print(f"Yoga: {panchanga['yoga'][1]} (#{panchanga['yoga'][0]})")
        print(f"Karana: {panchanga['karana'][1]} (#{panchanga['karana'][0]})")

        lunar, solar = check_eclipse(jd)
        if lunar and abs(lunar - jd) < 1:
            print("Eclipse Info: Lunar Eclipse")
        elif solar and abs(solar - jd) < 1:
            print("Eclipse Info: Solar Eclipse")
        else:
            print("Eclipse Info: No Eclipse")

        risk = travel_risk_level(panchanga, target_date.weekday(), jd)
        print("Travel Risk Level:", risk)

if __name__ == "__main__":
    main()
