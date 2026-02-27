import json
import threading
from time import sleep
from flask import Flask, render_template, request, redirect
from gpiozero import OutputDevice

from process.brew_process import BrewProcess
from controller.controller_preheat import PreheatController
from controller.controller_brew import BrewController
from controller.controller_boil import BoilController
from temp.temperature import temperature

app = Flask(__name__)

# ======================
# Hardware
# ======================

HEATER_PIN = 5
heater = OutputDevice(HEATER_PIN)

SENSOR_1 = "28-00000050b91c"
SENSOR_2 = "28-00000052834d"

# ======================
# States
# ======================

STATE_IDLE = "IDLE"
STATE_PREHEAT = "PREHEAT"
STATE_WAIT_FOR_MALT = "WAIT_FOR_MALT"
STATE_BREWING = "BREWING"
STATE_BOIL = "BOIL"

system_state = STATE_IDLE
brew_process = BrewProcess()
preheat_controller = None
brew_controller = None
boil_controller = None

current_temp1 = 0
current_temp2 = 0
current_avg = 0
current_power = 0
current_setpoint = 0


# ======================
# Control Loop
# ======================

def control_loop():
    global system_state
    global current_temp1, current_temp2, current_avg
    global current_power
    global preheat_controller, brew_controller
    global current_setpoint

    while True:

        # 1️⃣ Temperatur lesen
        measure = temperature(SENSOR_1, SENSOR_2)
        current_temp1 = measure[0]
        current_temp2 = measure[1]
        current_avg = measure[2]

        # 2️⃣ PREHEAT
        if system_state == STATE_PREHEAT and preheat_controller:
            current_setpoint = preheat_controller.setpoint

            current_power = preheat_controller.calculate_control_signal(current_temp2)
            preheat_controller.control_heater(current_power)

            if current_temp2 >= preheat_controller.setpoint - 0.3:
                system_state = STATE_WAIT_FOR_MALT

        # 3️⃣ BREW
        elif system_state == STATE_BREWING and brew_controller:
            target = brew_process.update(current_temp2)

            if target is not None:

                if target != brew_controller.setpoint:
                    print("Neue Rast:", target)
                    brew_controller.setpoint = target
                    brew_controller.integral = 0

                # 👉 GANZ WICHTIG:
                current_setpoint = brew_controller.setpoint

                current_power = brew_controller.calculate_control_signal(current_temp2)
                brew_controller.control_heater(current_power)

            else:
                current_power = 0

        elif system_state == STATE_BOIL and boil_controller:
            current_setpoint = 100.0  # Anzeige

            current_power = boil_controller.control(current_avg)
            boil_controller.apply(current_power)

        else:
            sleep(1)

        print("Power:", current_power)
    
    

threading.Thread(target=control_loop, daemon=True).start()


# ======================
# Web Routes
# ======================

@app.route("/")
def index():
    return render_template(
        "recipe.html",
        state=system_state,
        profile=brew_process.get_profile()
    )


@app.route("/brew")
def brew():
    remaining_time = brew_process.get_remaining_time()

    return render_template(
        "brew.html",
        state=system_state,
        temp1=round(current_temp1, 2),
        temp2=round(current_temp2, 2),
        avg=round(current_avg, 2),
        setpoint=round(current_setpoint, 2),
        power=round(current_power, 2),
        remaining=remaining_time
    )

@app.route("/load_json", methods=["POST"])
def load_json():
    file = request.files.get("json_file")

    if not file:
        return "Keine Datei gewählt", 400

    content = file.read().decode("utf-8-sig")
    recipe = json.loads(content)

    mash_profile = []

    # Durchsuche alle möglichen Rastfelder
    for i in range(1, 20):

        temp_key = f"Infusion_Rasttemperatur{i}"
        time_key = f"Infusion_Rastzeit{i}"

        if temp_key in recipe and time_key in recipe:

            temp_val = recipe[temp_key]
            time_val = recipe[time_key]

            if temp_val and time_val:
                mash_profile.append({
                    "temp": float(temp_val),
                    "time": int(time_val)
                })

    if not mash_profile:
        return "Kein gültiges Maischprofil im Rezept gefunden", 400

    brew_process.load_recipe({"mash_profile": mash_profile})

    print("Rezept erfolgreich konvertiert:")
    print(mash_profile)

    return redirect("/")

@app.route("/start_preheat", methods=["POST"])
def start_preheat():
    global system_state, preheat_controller, current_setpoint

    temps = request.form.getlist("temp[]")
    times = request.form.getlist("time[]")

    mash_profile = []

    for t, ti in zip(temps, times):

        # Leere Felder überspringen
        if not t.strip() or not ti.strip():
            continue

        mash_profile.append({
            "temp": float(t),
            "time": int(ti)
        })

    if not mash_profile:
        return "Kein gültiges Maischprofil angegeben", 400

    brew_process.load_recipe({"mash_profile": mash_profile})

    first_temp = brew_process.get_first_temp()

    if first_temp is None:
        return "Kein Rezept geladen", 400

    preheat_controller = PreheatController(heater, first_temp)

    current_setpoint = first_temp
    system_state = STATE_PREHEAT

    return redirect("/brew")


@app.route("/add_malt", methods=["POST"])
def add_malt():
    global brew_controller, preheat_controller
    global system_state, current_setpoint

    if not brew_process.mash_profile:
        return "Kein Maischprofil geladen", 400

    first_temp = brew_process.mash_profile[0]["temp"]

    brew_controller = BrewController(heater, first_temp)

    current_setpoint = first_temp
    system_state = STATE_BREWING

    return redirect("/brew")

@app.route("/start_boil", methods=["POST"])
def start_boil():
    global boil_controller, brew_controller, system_state

    boil_controller = BoilController(heater)

    system_state = STATE_BOIL

    return redirect("/brew")

if __name__ == "__main__":
    threading.Thread(target=control_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False)