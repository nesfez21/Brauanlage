import time
import csv
from gpiozero import OutputDevice
from controller.controller_preheat import PreheatController
from temp.temperature import temperature


# ================= KONFIGURATION =================

HEATER_PIN = 5

SENSOR_1 = "28-00000050b91c"
SENSOR_2 = "28-00000052834d"

SETPOINTS = [45, 70, 90]       # Zieltemperaturen
HOLD_TIME = 15 * 60            # 15 Minuten Haltezeit
TOLERANCE = 1.0                # ±1°C Bereich

CSV_FILE = "hold_test.csv"

# =================================================


heater = OutputDevice(HEATER_PIN)
controller = PreheatController(heater, SETPOINTS[0])

print("Starte Halteversuch...\n")

start_of_test = time.time()

with open(CSV_FILE, mode="w", newline="") as file:

    # ✅ Semikolon als Trennzeichen für Excel (DE)
    writer = csv.writer(file, delimiter=";")

    writer.writerow(["time_since_start_s", "sensor2_temp_C", "setpoint"])

    for sp in SETPOINTS:

        print(f"\nNeue Solltemperatur: {sp} °C")

        controller.setpoint = sp
        controller.integral = 0

        holding_started = False
        hold_start_time = None

        while True:

            # ===== Temperatur messen =====
            t1, t2, avg = temperature(SENSOR_1, SENSOR_2)

            # ===== Regelung (blockiert ~5s wegen PWM) =====
            power = controller.calculate_control_signal(t2)
            controller.control_heater(power)

            # ===== Zeit seit Beginn =====
            current_time = time.time()
            time_since_start = current_time - start_of_test

            # ===== CSV schreiben =====
            writer.writerow([
                round(time_since_start, 2),
                round(t2, 3),
                sp
            ])

            print(
                f"t={time_since_start:8.1f}s | "
                f"Temp={t2:6.2f}°C | "
                f"SP={sp:3}°C | "
                f"P={power:6.2f}%"
            )

            # ===== Haltebedingung prüfen =====
            if abs(t2 - sp) <= TOLERANCE:

                if not holding_started:
                    hold_start_time = time.time()
                    holding_started = True
                    print(">> Haltephase gestartet")

                elapsed_hold = time.time() - hold_start_time

                if elapsed_hold >= HOLD_TIME:
                    print(">> Haltezeit erreicht")
                    break

            else:
                # Temperatur außerhalb → Haltezeit neu starten
                holding_started = False

        print(f"Temperatur {sp} °C abgeschlossen.")

heater.off()
print("\nTest abgeschlossen.")