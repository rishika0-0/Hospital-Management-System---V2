from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from models import db, DoctorAvailability
import re
from datetime import date, timedelta, datetime, time as dt_time
import redis
import json

redis_cache = redis.Redis(host='localhost', port=6379, db=0)
CACHE_TTL = 300 

WEEKDAY_MAP = {
    "Mon": 0,
    "Tue": 1,
    "Wed": 2,
    "Thu": 3,
    "Fri": 4,
    "Sat": 5,
    "Sun": 6,
}

def parse_availability_string(avail_str: str):
    """
    Expected format: 'Mon-Fri: 09:00-13:00'
    Returns (start_weekday, end_weekday, start_time, end_time) or None.
    """
    if not avail_str:
        return None

    avail_str = avail_str.replace("–", "-")

    # Format: 'Mon-Fri: 09:00-13:00'
    pattern = r"([A-Za-z]{3})-([A-Za-z]{3})\s*:\s*([0-9]{2}:[0-9]{2})-([0-9]{2}:[0-9]{2})"
    m = re.match(pattern, avail_str.strip())
    if not m:
        print("Availability format invalid:", avail_str)
        return None

    start_day, end_day, start_t_str, end_t_str = m.groups()

    if start_day not in WEEKDAY_MAP or end_day not in WEEKDAY_MAP:
        print("Unknown weekday in availability:", start_day, end_day)
        return None

    start_weekday = WEEKDAY_MAP[start_day]
    end_weekday = WEEKDAY_MAP[end_day]

    start_hour, start_minute = map(int, start_t_str.split(":"))
    end_hour, end_minute = map(int, end_t_str.split(":"))

    start_time = dt_time(start_hour, start_minute)
    end_time = dt_time(end_hour, end_minute)

    if datetime.combine(date.today(), end_time) <= datetime.combine(date.today(), start_time):
        print("End time must be after start time:", avail_str)
        return None

    return start_weekday, end_weekday, start_time, end_time


def regenerate_availability_slots(doctor):
    
    parsed = parse_availability_string(doctor.availability)
    if not parsed:
        print("Could not parse availability for doctor", doctor.id, doctor.availability)
        return

    start_wd, end_wd, start_time, end_time = parsed

    today = date.today()
    week_later = today + timedelta(days=7)

    DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_later
    ).delete()
    db.session.commit()

    day_count = (week_later - today).days + 1
    for offset in range(day_count):
        current_date = today + timedelta(days=offset)
        wd = current_date.weekday() 

        if start_wd <= end_wd:
            in_range = start_wd <= wd <= end_wd
        else:
            in_range = wd >= start_wd or wd <= end_wd

        if not in_range:
            continue

        start_dt = datetime.combine(current_date, start_time)
        end_dt = datetime.combine(current_date, end_time)

        current = start_dt
        while current + timedelta(hours=1) <= end_dt:
            slot_start = current.time()
            slot_end = (current + timedelta(hours=1)).time()

            slot = DoctorAvailability(
                doctor_id=doctor.id,
                date=current_date,
                start_time=slot_start,
                end_time=slot_end,
                is_available=True
            )
            db.session.add(slot)
            current += timedelta(hours=1)

    db.session.commit()
    print(f"Regenerated slots for doctor {doctor.id} for next 7 days.")


migrate = Migrate()
jwt=JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from routes.auth import auth_blueprint as auth
    from routes.admin import admin_blueprint as admin
    from routes.doctor import doctor_blueprint as doc
    from routes.patient import patient_blueprint as patient

    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(doc)
    app.register_blueprint(patient)

    @app.route("/api/health")
    def check():
        return {"status": "ok", "message": "HMS API running"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)