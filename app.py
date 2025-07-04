from flask import Flask, render_template, request, redirect
import swisseph as swe
import datetime
from timezonefinder import TimezoneFinder
from datetime import date
import pytz
import csv
import os
import random

app = Flask(__name__)

# Set Swiss Ephemeris data path
swe.set_ephe_path(os.path.join(os.getcwd(), "ephe"))
swe.set_sid_mode(swe.SIDM_LAHIRI)

nakshatras = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya",
    "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

affirmations = [
    "I am aligned with the energy of the moon.",
    "I allow emotional healing to flow through me.",
    "I embrace peace and inner calm.",
    "I trust my intuition fully.",
    "I am deeply grounded and emotionally balanced.",
    "I let go of what no longer serves me.",
    "I welcome positive change with an open heart.",
    "My soul is nourished by love and truth.",
    "I honor my emotions without judgment.",
    "I shine with inner light and compassion."
]

moon_traits = {
    "Aries": "Energetic, bold, initiator",
    "Taurus": "Grounded, patient, sensual",
    "Gemini": "Adaptable, talkative, curious",
    "Cancer": "Nurturing, emotional, intuitive",
    "Leo": "Creative, proud, generous",
    "Virgo": "Analytical, modest, health-conscious",
    "Libra": "Balanced, diplomatic, artistic",
    "Scorpio": "Intense, secretive, emotional depth",
    "Sagittarius": "Optimistic, adventurous, wise",
    "Capricorn": "Ambitious, disciplined, practical",
    "Aquarius": "Inventive, independent, humanitarian",
    "Pisces": "Compassionate, dreamy, spiritual"
}

def get_daily_prediction(moon_sign):
    traits = moon_traits.get(moon_sign, "Empathetic and thoughtful.")

    # You can customize this per zodiac sign if you want accurate trends
    love_rating = {
        "Aries": random.randint(6, 9),
        "Taurus": random.randint(7, 10),
        "Gemini": random.randint(5, 8),
        "Cancer": random.randint(8, 10),
        "Leo": random.randint(6, 9),
        "Virgo": random.randint(5, 8),
        "Libra": random.randint(7, 10),
        "Scorpio": random.randint(6, 10),
        "Sagittarius": random.randint(5, 9),
        "Capricorn": random.randint(4, 7),
        "Aquarius": random.randint(5, 8),
        "Pisces": random.randint(8, 10)
    }.get(moon_sign, random.randint(5, 9))

    return {
        "overall": random.randint(3, 5),
        "energy": random.choice(["Low", "Medium", "High"]),
        "mental": random.choice(["Focused", "Distracted", "Clear"]),
        "physical": random.choice(["Energetic", "Tired", "Balanced"]),
        "love": love_rating,  
        "good_news": random.choice([
            "You might receive a compliment.",
            "Something unexpected will work out.",
            "A message may uplift your mood."
        ]),
        "caution": random.choice([
            "Don’t overthink things.",
            "Stay calm",
            "Avoid unnecessary drama."
        ]),
        "description": f"Today your Moon sign ({moon_sign}) brings {traits.lower()} energy. Trust yourself and go with the flow."
    }



def get_timezone(lat, lon):
    return TimezoneFinder().timezone_at(lat=lat, lng=lon)

def get_daily_affirmation():
    index = date.today().toordinal() % len(affirmations)
    return affirmations[index]

def get_moon_profile(dob, tob, lat, lon):
    year, month, day = map(int, dob.split('-'))
    hour, minute = map(int, tob.split(':'))
    local_tz = pytz.timezone(get_timezone(lat, lon))
    dt_local = datetime.datetime(year, month, day, hour, minute)
    dt_utc = local_tz.localize(dt_local).astimezone(pytz.utc)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0)
    moon_long = swe.calc_ut(jd, swe.MOON)[0][0]
    moon_long = (moon_long - swe.get_ayanamsa_ut(jd)) % 360
    moon_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    moon_sign = moon_signs[int(moon_long // 30)]
    nakshatra = nakshatras[int(moon_long // (360 / 27))]
    traits = moon_traits.get(moon_sign, "Empathetic and thoughtful.")
    return moon_sign, nakshatra, traits

@app.route('/')
def home():
    today = datetime.date.today()
    moon_long = swe.calc_ut(swe.julday(today.year, today.month, today.day), swe.MOON)[0][0]
    nakshatra = nakshatras[int(moon_long // (360 / 27))]
    moon_sign = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"][int(moon_long // 30)]
    traits = moon_traits.get(moon_sign, "")
    return render_template('home.html', nakshatra=nakshatra, traits=traits)

@app.route('/MyAstro', methods=['POST'])
def MyAstro():
    dob = request.form['dob']
    hour = int(request.form['hour'])
    minute = int(request.form['minute'])
    ampm = request.form['ampm']
    if ampm == "PM" and hour != 12:
        hour += 12
    elif ampm == "AM" and hour == 12:
        hour = 0
    tob = f"{hour:02d}:{minute:02d}"
    place = request.form['place']
    lat, lon = 25.40, 78.28
    moon_sign, nakshatra, traits = get_moon_profile(dob, tob, lat, lon)
    today_prediction = get_daily_prediction(moon_sign)
    affirmation = get_daily_affirmation()
    return render_template('moon_result.html', dob=dob, tob=tob, place=place,
                        moon_sign=moon_sign, nakshatra=nakshatra,
                        traits=traits, prediction=today_prediction,
                        affirmation=affirmation)

@app.route('/feedback', methods=['POST'])
def feedback():
    rating = request.form['rating']
    comment = request.form['comment']
    with open('feedbacks.csv', 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([rating, comment])
    return redirect('/')

@app.route('/journal', methods=['GET', 'POST'])
def journal():
    mood_map = {
        "Very Sad": 1, "Sad": 2, "Neutral": 3,
        "Happy": 4, "Very Happy": 5,
        "Calm": 3, "Anxious": 2, "Overthinking": 2, "Motivated": 4
    }
    if request.method == 'POST':
        mood_text = request.form['mood']
        mood_value = mood_map.get(mood_text, 3)
        entry = request.form['entry']
        today = datetime.date.today().strftime('%Y-%m-%d')
        with open('mood_data.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([today, mood_value, mood_text, entry])
        return redirect('/')
    return render_template('journal.html')

@app.route('/dashboard')
def dashboard():
    dates, moods = [], []
    try:
        with open('mood_data.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    try:
                        dates.append(row[0])
                        moods.append(int(row[1]))
                    except ValueError:
                        continue
    except FileNotFoundError:
        dates = ['2025-06-28', '2025-06-29', '2025-06-30']
        moods = [3, 4, 2]
    return render_template('dashboard.html', dates=dates, moods=moods)

@app.route('/healing')
def healing():
    affirmations = [
        "I am calm and grounded.", "I trust the timing of my life.",
        "I release all that no longer serves me.",
        "I deserve love and inner peace.", "Everything is unfolding perfectly."
    ]
    chosen = random.choice(affirmations)
    return render_template('healing.html', affirmation=chosen)

@app.route('/forecast')
def forecast():
    today = datetime.date.today()
    jd = swe.julday(today.year, today.month, today.day)
    moon_long = swe.calc_ut(jd, swe.MOON)[0][0]
    moon_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    nakshatra = nakshatras[int(moon_long // (360 / 27))]
    moon_sign = moon_signs[int(moon_long // 30)]
    message = f"Let your {moon_traits.get(moon_sign, '').lower()} side shine today."
    return render_template("forecast.html", date=today, moon_sign=moon_sign, nakshatra=nakshatra, message=message)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8000)
