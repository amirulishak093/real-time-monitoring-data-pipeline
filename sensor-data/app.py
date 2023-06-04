import os
import random
from datetime import datetime
import threading
import time
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

load_dotenv(".env")

api_key = os.getenv("API_KEY")
db_name = os.getenv("DB_NAME")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_name}.db"
db = SQLAlchemy(app)

# Lock for synchronizing database access
db_lock = threading.Lock()


class Zone(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True)
    sensors = relationship("Sensor", backref="zone", lazy=True)


class Sensor(db.Model):
    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("zone.id"))
    temperature = Column(Float)
    humidity = Column(Float)
    air_quality = Column(Float)
    recorded_at = Column(DateTime)


def init_db():
    with app.app_context():
        db.create_all()


def generate_sensor_data(recorded_at: datetime):
    temperature = random.uniform(20.0, 25.0)
    humidity = random.uniform(50.0, 60.0)
    air_quality = random.randint(20, 60)
    return Sensor(
        temperature=temperature,
        humidity=humidity,
        air_quality=air_quality,
        recorded_at=recorded_at,
    )


def get_or_create_zone(name: str) -> Zone:
    with db_lock:
        zone = Zone.query.filter_by(name=name).first()
        if zone is None:
            zone = Zone(name=name)
            db.session.add(zone)
            db.session.commit()
    return zone


def add_data(zone: Zone, data: Sensor):
    with db_lock:
        zone.sensors.append(data)
        db.session.add(data)
        db.session.commit()


def run_sensor(zone_name: str):
    with app.app_context():
        zone = get_or_create_zone(zone_name)
        while True:
            print(f"Adding sensor data for {zone_name}")
            sensor_data = generate_sensor_data(datetime.now())
            add_data(zone, sensor_data)
            time.sleep(5)


def run_all_sensors(zone_names: list[str]):
    with app.app_context():
        zones = []

        for zone_name in zone_names:
            zones.append(get_or_create_zone(zone_name))

        while True:
            current_time = datetime.now()
            for zone in zones:
                print(f"Adding sensor data for {zone.name}")
                sensor_data = generate_sensor_data(current_time)
                add_data(zone, sensor_data)

            time.sleep(5)


def is_token_valid(access_token: str) -> bool:
    if access_token == api_key:
        return True
    else:
        return False


# Token verification middleware
# Doesn't implement the actual token-based security
@app.before_request
def verify_access_token():
    # Get the access token from the request headers
    access_token = request.headers.get("Authorization")

    # Verify the access token
    if not access_token:
        return jsonify({"message": "Missing access token"}), 401

    if not is_token_valid(access_token):
        return jsonify({"message": "Invalid access token"}), 401


@app.route("/")
def home():
    return "Sensor data addition in progress."


@app.route("/sensor-data", methods=["GET"])
def get_sensor_data():
    zone_name = request.args.get("zone_name")
    if zone_name:
        with db_lock:
            zone = Zone.query.filter_by(name=zone_name).first()
            if zone:
                latest_sensor = (
                    Sensor.query.filter_by(zone_id=zone.id)
                    .order_by(Sensor.id.desc())
                    .first()
                )
                if latest_sensor:
                    return jsonify(
                        {
                            "air_quality": latest_sensor.air_quality,
                            "humidity": latest_sensor.humidity,
                            "recorded_at": latest_sensor.recorded_at.strftime(
                                "%Y-%m-%dT%H:%M:%S"
                            )
                            + "Z",
                            "temperature": latest_sensor.temperature,
                            "zone_name": zone.name,
                        }
                    )
    return jsonify({})


if __name__ == "__main__":
    init_db()

    zone_names = ["ed", "icu", "lab", "cd", "rd"]

    # Run all sensors in multiple threads
    # zone_threads = []

    # for zone_name in zone_names:
    #     thread = threading.Thread(target=run_sensor, daemon=True, args=[zone_name])
    #     zone_threads.append(thread)
    #     thread.start()

    # Run all sensors in a single thread
    all_sensors_thread = threading.Thread(
        target=run_all_sensors, daemon=True, args=[zone_names]
    )
    all_sensors_thread.start()

    app.run(host="0.0.0.0", port=2800)
