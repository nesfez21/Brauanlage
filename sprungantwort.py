import time
import csv
from gpiozero import OutputDevice
from temp.read_temperature import temp_read  # dein Modul

# ======================
# Einstellungen
# ======================
HEATER_PIN = 5
POWER_PERCENT = 20
WINDOW_TIME = 5.0
SENSOR_2 = "28-00000052834d"

CSV_FILENAME = "sprungantwort_20.csv"

# ======================
# Initialisierung
# ======================
heater = OutputDevice(HEATER_PIN)
start_time = time.time()

print("Sprungantwort gestartet (Excel-kompatibel).")
print("STRG+C zum Beenden.\n")

with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file, delimiter=";")  # <-- WICHTIG für Excel (DE)
    writer.writerow(["time_s", "temp_C"])

    try:
        while True:

            # ---- konstante Heizleistung ----
            on_time = (POWER_PERCENT / 100.0) * WINDOW_TIME
            off_time = WINDOW_TIME - on_time

            if on_time > 0:
                heater.on()
                time.sleep(on_time)

            if off_time > 0:
                heater.off()
                time.sleep(off_time)

            # ---- Temperatur messen ----
            current_time = time.time() - start_time
            temp2 = temp_read(SENSOR_2)

            writer.writerow([str(round(current_time, 2)).replace(".", ","),
                 str(round(temp2, 3)).replace(".", ",")])
            file.flush()

            print(f"{current_time:.1f}s | T2={temp2:.2f}°C")

    except KeyboardInterrupt:
        heater.off()
        print("\nMessung beendet.")