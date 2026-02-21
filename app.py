from flask import Flask, render_template, jsonify, request
import threading
import time

from controller.controller_preheat import PreheatController
from controller.controller_brew import BrewController
from process.brew_process import BrewProcess
from temperature import temperature

# --------------------------------------------------
# KONFIGURATION
# --------------------------------------------------

SENSOR_1 = "28-00000050b91c"
SENSOR_2 = "28-00000052834d"

HEATER_PIN = 5

PREHEAT_SETPOINT = 60.0

# Beispiel Maischprofil
DEFAULT_MASH_PROFILE = [
    {"temp": 63, "time": 30},
    {"temp": 72, "time": 20},
]

# --------------------------------------------------
# INITIALISIERUNG
# --------------------------------------------------

app = Flask(__name__)

preheat_controller = PreheatController(HEATER_PIN, PREHEAT_SETPOINT)
brew_controller = BrewController(HEATER_PIN, PREHEAT_SETPOINT)

brew = BrewProcess(preheat_controller, brew_controller)
brew.load_mash_profile(DEFAULT_MASH_PROFILE)

# --------------------------------------------------
# REGELTHREAD
# --------------------------------------------------

def control_loop():
    while True:
        measure = temperature(SENSOR_1, SENSOR_2)

        # Mittelwert
        avg_temp = (measure[0] + measure[1]) / 2

        brew.update(avg_temp)

        time.sleep(1)


thread = threading.Thread(target=control_loop, daemon=True)
thread.start()

# --------------------------------------------------
# ROUTES
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("brew.html")


@app.route("/api/status")
def status():
    return jsonify(brew.get_status())


@app.route("/start_preheat", methods=["POST"])
def start_preheat():
    brew.start_preheat(PREHEAT_SETPOINT)
    return ("", 204)


@app.route("/start_mash", methods=["POST"])
def start_mash():
    brew.start_mash()
    return ("", 204)


# --------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)